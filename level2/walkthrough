# Level2 - Exam Notes

## 1. Objective
Obtenir un shell level3. Binaire setuid level3 ; pas de system dans le flux normal. Il faut exécuter du shellcode (ex. execve("/bin/sh")).

## 2. Initial diagnosis (before GDB)
- **Fonctions suspectes :** `gets` dans `p()` ; pas de system. Buffer à ebp-0x4c, lecture de l’adresse de retour puis test `(ret & 0xb0000000) == 0xb0000000` → si oui, exit. Donc pas de retour direct vers la stack (adresses 0xb...).
- **Entrée utilisateur :** tout ce que gets lit dans le buffer ; sans limite.
- **Succès :** exécuter du shellcode (ex. execve("/bin/sh")) ; le shellcode doit être dans le buffer, mais on ne peut pas mettre 0xb... en ret. Il faut un gadget (ex. pop; ret) pour faire un second saut vers le buffer.
- **Hypothèse :** buffer overflow ; retour vers un gadget dans le binaire, puis deux mots = adresse du buffer pour que le ret du gadget saute au buffer (shellcode).

## 3. GDB diagnosis (how the vulnerability was found)
- **Où break :** dans `p`, après gets (ou avant le ret de p). But : mesurer l’offset et confirmer le gadget.
- **Layout stack :** buffer à `ebp-0x4c` → 76 octets jusqu’à saved EBP, +4 = **80 octets** jusqu’à l’adresse de retour. `x/24wx $ebp-0x4c` pour voir buffer, EBP, ret.
- **Offset :** 80 octets (calculé : 0x4c + 4). Vérification : envoyer 80 octets + 0x42424242 ; segfault en 0x42424242 confirme.
- **Gadget :** dans le binaire, chercher `pop reg; ret` (ex. objdump -d | grep -A1 pop). **0x08048385** : `pop ebx; ret`. En retournant ici : le pop consomme le premier mot (on met l’adresse du buffer), le ret saute au deuxième mot (encore l’adresse du buffer) → exécution du code au début du buffer.
- **Adresse du buffer :** sans ASLR (VM 32b), après avoir envoyé une entrée, `info frame` ou `x/s $esp` ; adresse typique **0xbffff6c0** (sinon 0xbffff660, 0xbffff710). À noter pour le payload.
- **Contrôle du flux :** payload = [shellcode][padding jusqu’à 80][0x08048385][addr_buf][addr_buf]. Au ret de p → gadget ; pop consomme addr_buf ; ret saute à addr_buf → shellcode.

## 4. Building the exploit command
- **Cible :** après 80 octets, écraser l’adresse de retour par le gadget 0x08048385 ; puis deux mots = adresse du buffer (shellcode).
- **Structure :** [shellcode ~25–30 octets][padding pour total 80][\x85\x83\x04\x08][addr_buf LE][addr_buf LE]. Shellcode execve("/bin/sh") sans NUL ni \n.
- **Encodage :** adresses en LE. Buffer ex. 0xbffff6c0 → `\xc0\xf6\xff\xbf`. Python pour shellcode + padding + adresses.
- **Invocation :** stdin ; garder le shell ouvert : `( python -c '...'; cat ) | ./level2`. Adresse du buffer à adapter selon GDB (x/s environ ou adresse du buffer après entrée).
- **Référence commands.md :** commande finale dans `commands.md`, section « Exploitation ». Les valeurs 80, 0x08048385 et l’adresse du buffer viennent du diagnostic GDB.

## 5. Exploitation logic
Overflow via gets() ; contrainte : ret ne doit pas être 0xb... (sinon exit). On retourne vers un gadget pop; ret ; on met deux fois l’adresse du buffer pour que le ret du gadget saute au buffer ; au début du buffer, shellcode → shell.

## 6. Reproducible procedure (for evaluation)
- **Commande :** selon `commands.md` (Exploitation), avec l’adresse buffer trouvée en GDB. Ex. : `( python -c 'print "<shellcode>" + "A"*(80-len(shellcode)) + "\x85\x83\x04\x08" + "\xc0\xf6\xff\xbf"*2'; cat ) | ./level2`.
- **Résultat attendu :** shell level3. Puis `cat /home/user/level3/.pass`.
- **À dire :** « gets() overflow. Le programme refuse une ret en 0xb..., donc je retourne vers un gadget pop;ret et je mets deux fois l’adresse du buffer pour sauter au shellcode. »

## 7. Oral defense points
- **Bug :** gets() dans p() sans limite ; overflow sur la stack.
- **Contrainte :** ret & 0xb0000000 → exit ; pas de retour direct au buffer.
- **GDB :** offset 80, gadget 0x08048385, adresse du buffer (ex. 0xbffff6c0).
- **Fix :** remplacer gets par fgets avec taille bornée.

## 8. Common evaluator questions
- **Pourquoi un gadget ?** L’adresse du buffer est 0xb... ; le programme quitte si ret dans cette plage. Le gadget est en 0x08... ; le ret du gadget lit la prochaine valeur sur la stack (notre adresse buffer) et y saute.
- **Que fait le gadget ?** pop consomme un mot (on met l’adresse buffer), ret saute au mot suivant (encore l’adresse buffer) → exécution du buffer.
- **Comment trouves-tu l’adresse du buffer ?** En GDB, après avoir envoyé une entrée, regarder l’adresse du buffer (info frame, x $esp) ; VM 32b sans ASLR donne une adresse stable (ex. 0xbffff6c0).
- **Shellcode sans NUL ?** gets s’arrête au \n ; et un NUL couperait strdup/affichage ; un shellcode classique sans NUL évite les coupures.
