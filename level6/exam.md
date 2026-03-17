# Level6 - Exam Notes

## 1. Objective
Afficher le mot de passe level7. Le binaire est setuid level7 ; `n()` exécute `system("/bin/cat /home/user/level7/.pass")` mais n’est pas appelée. Par défaut un pointeur de fonction pointe vers `m()` ("Nope").

## 2. Initial diagnosis (before GDB)
- **Fonctions suspectes :** `strcpy(buffer, argv[1])` sans limite dans main ; buffer = malloc(64), puis malloc(4) pour un pointeur de fonction ; *ptr = m ; **call *ptr**. Overflow possible depuis le buffer vers le bloc suivant (pointeur).
- **Entrée utilisateur :** argv[1] copié intégralement dans le buffer par strcpy.
- **Succès :** faire en sorte que call *ptr invoque n() au lieu de m() → affichage du mot de passe. Donc écraser le pointeur par l’adresse de n (0x08048454).
- **Hypothèse :** buffer overflow sur le heap ; le pointeur est juste après le buffer (avec en-têtes de chunk). Sur Rainfall l’offset observé est **72** (64 + 8).

## 3. GDB diagnosis (how the vulnerability was found)
- **Où break :** dans main, juste avant `call *ptr` (ou avant l’instruction qui charge le pointeur). But : voir la valeur du pointeur avant/après overflow et confirmer l’offset.
- **Layout heap :** main fait malloc(0x40) puis malloc(4). Le buffer fait 64 octets ; le bloc de 4 contient le pointeur. Selon l’allocateur, il peut y avoir des en-têtes entre les deux. `x/20wx` sur les adresses retournées par malloc pour voir buffer puis pointeur. Sur Rainfall : **72 octets** (64 + 8) pour atteindre les 4 octets du pointeur.
- **Offset :** envoyer 72 octets + 4 octets (ex. adresse de n). Break avant call *ptr ; le registre (ex. eax) doit contenir 0x08048454. Si le programme appelle n() et affiche le mot de passe, l’offset 72 est correct. Sinon tester 64 ou 68.
- **Adresses :** `info functions` ou désassemblage : n @ **0x08048454**, m @ 0x08048468.
- **Contrôle du flux :** call *ptr lit la valeur du pointeur ; après overflow avec 72 + \x54\x84\x04\x08, cette valeur est 0x08048454 → exécution de n() → system("/bin/cat ...").

## 4. Building the exploit command
- **Cible :** le pointeur de fonction (4 octets après 72 octets de padding) ; valeur : adresse de n = 0x08048454.
- **Structure :** [72 octets padding] + [4 octets = 0x08048454 LE]. Pas de shellcode ; uniquement padding + adresse.
- **Encodage :** `\x54\x84\x04\x08`. Python : `print "A"*72 + "\x54\x84\x04\x08"`. Pas de \n dans argv[1] (strcpy s’arrête au NUL, donc pas de problème).
- **Invocation :** le programme prend argv[1] ; pas de stdin à garder. `./level6 $(python -c 'print "A"*72 + "\x54\x84\x04\x08"')`.
- **Référence commands.md :** section Exploitation. La valeur 72 et l’adresse de n viennent du diagnostic GDB (layout heap).

## 5. Exploitation logic
Buffer overflow sur le heap via strcpy(buffer, argv[1]). Le pointeur de fonction est stocké juste après le buffer ; en l’écrasant avec l’adresse de n(), call *ptr invoque n() → /bin/cat affiche le mot de passe.

## 6. Reproducible procedure (for evaluation)
- **Commande :** `./level6 $(python -c 'print "A"*72 + "\x54\x84\x04\x08"')`. Le mot de passe level7 s’affiche.
- **Résultat attendu :** sortie = mot de passe level7.
- **À dire :** « strcpy sans limite ; le pointeur de fonction est à 72 octets (buffer 64 + en-tête). J’écrase ce pointeur avec l’adresse de n pour que call *ptr exécute n() et affiche le mot de passe. »

## 7. Oral defense points
- **Bug :** strcpy(buffer, argv[1]) sans contrôle de longueur ; buffer 64 octets (main).
- **GDB :** confirme que le pointeur est à l’offset 72 et que sa valeur devient 0x08048454 après overflow.
- **Payload :** 72 octets + adresse de n ; pas de shellcode.
- **Fix :** strncpy avec limite ou vérifier la longueur de argv[1].

## 8. Common evaluator questions
- **Pourquoi 72 et pas 64 ?** En-têtes de blocs malloc ou alignement ; sur la VM Rainfall 72 est l’offset observé en GDB.
- **Où est le pointeur ?** Dans le second bloc malloc(4), juste après le buffer de 64 octets sur le heap.
- **Stack ou heap ?** Heap : buffer et pointeur sont alloués par malloc.
- **Pourquoi n() ?** n() exécute /bin/cat .../.pass ; m() affiche seulement "Nope".
