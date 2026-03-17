# Bonus0 - Exam Notes

## 1. Objective
Obtenir un shell (ou lire `/home/user/bonus1/.pass`) en exploitant le binaire bonus0, qui lit **deux lignes** sur stdin et les concatène dans un buffer de 42 octets (strcpy(buf1) + " " + strcat(buf2)).

## 2. Initial diagnosis (before GDB)
- **Fonctions suspectes :** read(0, buf, 0x1000), strncpy(20), strcpy, strcat. Pas de vérification de longueur sur la concaténation. Buffer de main (dest) = 42 octets ; on écrit 20 + 2 + 20 = 42 octets + le `\0` final → overflow (au moins 1 octet au-delà du buffer : saved EBP puis adresse de retour).
- **Entrée utilisateur :** deux lignes ; la 2ᵉ ligne (buf2) contrôle ce qui écrase la stack après les 20+2 premiers octets. Contrainte : seulement 20 octets « utiles » par ligne pour le contenu, mais le null final de strcat écrit au-delà.
- **Succès :** écraser l’adresse de retour et la rediriger soit vers system("/bin/sh") (ret2libc) soit vers un nopsled/shellcode dans l’env (ret2env).
- **Hypothèse :** overflow par concaténation ; la 2ᵉ ligne doit contenir padding + adresse de retour écrasée. Problème : le premier read lit jusqu’à 4096 octets ; si on envoie 42 octets en une fois, le 2ᵉ read ne reçoit rien. D’où l’**astuce 4095** : 1ʳᵉ ligne = 4095 octets + `\n` (4096 total), 2ᵉ ligne = notre payload.

## 3. GDB diagnosis (how the vulnerability was found)
- **Où break :** à la fin de `pp`, juste avant le ret (ex. `break *0x80485a3`). But : mesurer l’offset du buffer (argument de pp = buffer de main) jusqu’à la saved EIP (saved return address de main).
- **Layout stack :** l’argument de pp (buffer de main) est à `ebp+8`. La saved EIP de main est à `ebp+4` (dans la frame de main, qui est juste au-dessus de la frame de pp). Donc **offset = (char*)(ebp+4) - (char*)*(void**)(ebp+8)**. En GDB : `p/x *(void**)($ebp+8)` (adresse du buffer), `p/x (char*)$ebp + 4` (adresse de la saved EIP), puis offset = différence en décimal. Sur la VM on obtient souvent un offset entre 28 et 46 (ex. 33 ou 38). Cela prouve combien d’octets remplissent le buffer jusqu’à l’adresse de retour.
- **Payload 4095 pour GDB :** créer un fichier : 1ʳᵉ ligne 4095 octets + `\n`, 2ᵉ ligne 20 octets + `\n`. `run < /tmp/payload` pour que le 1er read consomme 4096 octets et le 2ᵉ lise la 2ᵉ ligne. À la breakpoint, calculer l’offset comme ci-dessus.
- **Ret2env — adresse du nopsled :** `env -i payload=$PAYLOAD gdb ./bonus0`, `b main`, `r`, puis `x/500s environ`. Noter une adresse dans la zone des NOPs (ex. **0xbffffe57** ou 0xbffffd8f). Cette adresse sera utilisée en little endian dans la 2ᵉ ligne.
- **Structure 2ᵉ ligne (ret2env) :** offset = 9 + 4 (adresse) + 7 = 20 octets utiles avant le `\n`. Donc [9 octets padding] + [4 octets = adresse nopsled LE] + [7 octets] pour que l’adresse de retour soit exactement écrasée par notre adresse. Si l’offset GDB est différent (ex. 10 + 4 + 6), ajuster : padding + adresse + padding pour total = offset - 1 (ou jusqu’à ce que EIP soit couvert).
- **Contrôle du flux :** après overflow, au ret de main, eip = adresse du nopsled → exécution du shellcode → shell. Vérifier en lançant l’exploit avec le fichier généré.

## 4. Building the exploit command
- **Cible :** adresse de retour de main ; valeur : adresse du nopsled (ret2env) ou adresse de system (ret2libc). Ret2env est souvent plus fiable sur la VM (offset ret2libc variable).
- **Structure (ret2env) :** 1ʳᵉ ligne : 4095 octets + `\n`. 2ᵉ ligne : [9 octets] + [adresse nopsled 4 octets LE] + [7 octets] + `\n`. Ex. adresse 0xbffffe57 → `"\x57\xfe\xff\xbf"`. Fichier : `open("/tmp/file","wb").write("B"*4095+"\n"+"A"*9+"\x57\xfe\xff\xbf"+"B"*7+"\n")`.
- **Encodage :** adresse en LE. Pas de \n dans les 20 octets de la 2ᵉ ligne (sauf en fin de ligne).
- **Invocation :** `cat /tmp/file - | env -i payload=$PAYLOAD ./bonus0`. Le `-` garde stdin ouvert après le fichier pour pouvoir taper dans le shell. PAYLOAD = nopsled + shellcode (voir commands.md).
- **Référence commands.md :** section « GDB — Offset et adresses » pour la mesure de l’offset et l’astuce 4095 ; section « Alternative : ret2env » pour la définition de PAYLOAD, la création du fichier et la commande finale. Les valeurs 9 et 7 viennent de l’offset mesuré en GDB (offset - 4 - 4 = padding avant adresse et après, pour que les 4 octets au bon endroit soient l’adresse).

## 5. Exploitation logic
Overflow par strcpy + strcat : 20 + 2 + 20 + null écrits dans un buffer de 42 octets ; le null final et les octets de la 2ᵉ ligne dépassent et écrasent saved EBP puis l’adresse de retour. On contrôle la 2ᵉ ligne ; avec l’astuce 4095, le 2ᵉ read reçoit bien notre overflow. On écrase la ret par l’adresse du shellcode (env) → shell.

## 6. Reproducible procedure (for evaluation)
- **Préparer PAYLOAD** (nopsled + shellcode), voir commands.md.
- **En GDB :** trouver l’adresse du nopsled (`env -i payload=$PAYLOAD gdb ./bonus0`, `b main`, `r`, `x/500s environ`). Adapter les octets dans la 2ᵉ ligne si l’offset diffère (9 + 4 + 7).
- **Créer le fichier :** `python -c 'open("/tmp/file","wb").write("B"*4095+"\n"+"A"*9+"\x57\xfe\xff\xbf"+"B"*7+"\n")'` (remplacer \x57\xfe\xff\xbf par l’adresse trouvée en LE).
- **Commande :** `cat /tmp/file - | env -i payload=$PAYLOAD ./bonus0`, puis `cat /home/user/bonus1/.pass`.
- **Résultat attendu :** shell bonus0 (ou bonus1 selon le sujet), mot de passe affiché.
- **À dire :** « Le programme concatène deux lignes dans 42 octets ; le null final et la 2ᵉ ligne débordent et écrasent l’adresse de retour. J’utilise la 1ʳᵉ ligne de 4095 octets pour que le 2ᵉ read lise ma 2ᵉ ligne. J’écrase la ret par l’adresse du shellcode dans l’env. »

## 7. Oral defense points
- **Bug :** strcpy et strcat sans limite vers un buffer de 42 octets ; 20+2+20+null → overflow.
- **Où :** dans pp(), concaténation vers le buffer de main (dest).
- **GDB :** confirme l’offset (buffer → saved EIP) ; confirme l’adresse du nopsled via x/s environ. Astuce 4095 pour avoir deux lignes en GDB.
- **Payload :** 1ʳᵉ ligne 4095+\n ; 2ᵉ ligne = padding + adresse nopsled + padding. Fix : borner les copies (strncpy, vérifier la taille totale avant strcat).

## 8. Common evaluator questions
- **Pourquoi 4095 ?** read(0, buf, 0x1000) lit 4096 octets. Si la 1ʳᵉ ligne fait 4095+\n, le 1er read consomme tout ; le 2ᵉ read lit alors la 2ᵉ ligne. Sinon tout est lu d’un coup et la 2ᵉ ligne est vide.
- **Pourquoi ret2env ?** On ne contrôle que 20 octets par ligne ; la 2ᵉ ligne doit contenir padding + adresse. Mettre le shellcode dans l’env permet d’avoir une adresse stable (nopsled) sans ASLR.
- **Comment trouves-tu l’offset ?** En GDB, break à la fin de pp ; buffer = *(ebp+8), saved EIP à ebp+4 ; offset = (ebp+4) - buffer.
- **Pourquoi 9 + 4 + 7 ?** L’offset jusqu’à la saved EIP (mesuré en GDB) détermine combien d’octets avant les 4 de l’adresse ; 9+4+7 = 20 octets utilisés dans la 2ᵉ ligne. Ajuster selon l’offset réel.
