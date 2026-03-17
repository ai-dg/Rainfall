# Level4 - Exam Notes

## 1. Objective
Afficher le mot de passe level5. Le binaire est setuid level5 ; si `m` (0x8049810) vaut 0x1025544 (16930116), il exécute `system("/bin/cat /home/user/level5/.pass")`.

## 2. Initial diagnosis (before GDB)
- **Fonctions suspectes :** `p(buffer)` fait **printf(buffer)** → format string. Variable `m` @ 0x8049810 ; si m == 16930116 → /bin/cat affiche le mot de passe.
- **Entrée utilisateur :** buffer lu par fgets, passé à p() puis à printf.
- **Succès :** écrire 16930116 en mémoire à 0x8049810 via %n.
- **Hypothèse :** format string ; il faut trouver l’index k pour lequel l’argument de printf pointe vers notre buffer (où on mettra l’adresse de m), puis %16930112x%k$n (4+16930112=16930116).

## 3. GDB diagnosis (how the vulnerability was found)
- **Où break :** après printf dans p(), ou avant la lecture de m. But : vérifier la valeur de m et trouver l’index du buffer.
- **Index du buffer :** envoyer "AAAA" + "%1$p" + "%2$p" + … + "%15$p" (ou un fichier avec cette chaîne). Repérer quel %k$p affiche **0x41414141** (ou l’adresse du buffer). Sur l’ISO officielle **k = 12**. Cela prouve que le 12e argument pointe vers notre buffer (les 4 premiers octets "AAAA").
- **Adresse de m :** 0x8049810 (symbole ou readelf). On met cette adresse au début du buffer à la place de "AAAA".
- **Valeur à écrire :** 16930116 = 0x1025544. Avec un seul %n : on imprime 4 (adresse) + 16930112 = 16930116 caractères, puis %12$n écrit 16930116 à 0x8049810.
- **Contrôle du flux :** après printf, `x/wx 0x8049810` doit valoir 0x1025544 ; le programme exécute alors /bin/cat et affiche le mot de passe à la fin (sortie très longue).

## 4. Building the exploit command
- **Cible :** écrire 16930116 à l’adresse 0x8049810 (m).
- **Structure :** [4 octets = 0x8049810 LE] + "%16930112x" + "%12$n". L’index 12 vient du dump GDB (AAAA + %k$p). 4 + 16930112 = 16930116.
- **Encodage :** `\x10\x98\x04\x08`. Python : `print "\x10\x98\x04\x08" + "%16930112x%12$n"`.
- **Invocation :** `python -c '...' | ./level4`. Pas besoin de garder stdin ouvert (le programme affiche puis termine). Attendre 10–30 s (sortie ~16 Mo).
- **Référence commands.md :** section Exploitation. Si 12 ne marche pas sur une autre VM, refaire le dump pour trouver k et remplacer 12 par k.

## 5. Exploitation logic
Format string dans p() : printf(buffer). On met l’adresse de m au début du buffer ; l’argument à l’index 12 (trouvé par dump) pointe vers cette adresse. %16930112x%12$n écrit 16930116 à m → le programme lance /bin/cat et affiche le mot de passe.

## 6. Reproducible procedure (for evaluation)
- **Commande :** `python -c 'print "\x10\x98\x04\x08" + "%16930112x%12$n"' | ./level4`. Mot de passe level5 à la fin de la sortie.
- **Résultat attendu :** après un long délai, le mot de passe level5 s’affiche.
- **À dire :** « Format string ; j’ai trouvé l’index 12 avec AAAA + %k$p. J’écris 16930116 à l’adresse de m avec %16930112x%12$n. »

## 7. Oral defense points
- **Bug :** printf(buffer) dans p(), format string contrôlée par l’utilisateur.
- **GDB :** dump pour index 12 ; adresse de m 0x8049810 ; après exploit, m = 0x1025544.
- **Payload :** adresse m + %16930112x + %12$n.
- **Fix :** printf("%s", buffer).

## 8. Common evaluator questions
- **Pourquoi 16930112 ?** 16930116 - 4 (octets de l’adresse) ; %n écrit le nombre total d’octets imprimés.
- **Comment trouver 12 ?** Envoyez "AAAA" + "%1$p"... ; le k qui affiche 0x41414141 (ou l’adresse du buffer) est l’index du buffer.
- **Pourquoi la sortie est si longue ?** %16930112x imprime 16930112 caractères.
- **Où est m ?** 0x8049810 (variable globale).
