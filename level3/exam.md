# Level3 - Exam Notes

## 1. Objective
Obtenir un shell level4. Le binaire est setuid level4 ; la variable globale `m` doit valoir 64 pour que `system("/bin/sh")` soit appelé. `m` n’est jamais initialisée à 64 dans le code.

## 2. Initial diagnosis (before GDB)
- **Fonctions suspectes :** `fgets` puis **printf(buffer)** dans `v()` — l’entrée est utilisée comme chaîne de format (format string).
- **Entrée utilisateur :** buffer 512 octets lu par fgets, passé tel quel à printf.
- **Succès :** `m == 64` (0x40) à l’adresse 0x804988c → branche system("/bin/sh").
- **Hypothèse :** format string ; utiliser %n pour écrire 64 à l’adresse de m. Le 1er argument de printf est le buffer → %1$n écrit à l’adresse contenue au début du buffer.

## 3. GDB diagnosis (how the vulnerability was found)
- **Où break :** dans `v`, après l’appel à printf(buffer). But : vérifier que m (0x804988c) a bien été modifiée.
- **Layout :** pas d’overflow stack ; on s’intéresse à la variable globale. `x/wx 0x804988c` avant exploit → valeur initiale (souvent 0). Après payload avec adresse 0x804988c + "%60x%1$n" → `x/wx 0x804988c` doit valoir 0x40 (64). Cela prouve que %1$n écrit bien à l’adresse qu’on a mise au début du buffer.
- **Index du buffer :** le 1er argument de printf est notre chaîne (le buffer). Donc l’argument 1 pointe vers le début du buffer ; si les 4 premiers octets du buffer sont 0x804988c, alors %1$n écrit à cette adresse. Pas besoin de dump %1$p…%k$p pour ce level.
- **Valeur 64 :** %n écrit le nombre d’octets déjà imprimés. On imprime 4 (l’adresse) + 60 (avec "%60x") = 64, puis %1$n → 64 écrit à 0x804988c.
- **Contrôle du flux :** après printf, le code lit m ; si m == 64, il appelle system("/bin/sh"). Vérifier en single-step ou en relançant avec le payload.

## 4. Building the exploit command
- **Cible :** écrire la valeur 64 à l’adresse 0x804988c (variable m).
- **Structure du payload :** [4 octets = 0x804988c en LE] + "%60x" + "%1$n". Les 4 octets sont l’adresse où %1$n écrira ; "%60x" affiche 60 caractères (total 4+60=64) ; %1$n écrit 64 à 0x804988c.
- **Encodage :** adresse en little endian : `\x8c\x98\x04\x08`. Python : `print "\x8c\x98\x04\x08" + "%60x%1$n"`.
- **Invocation :** stdin ; garder le shell : `( python -c '...'; cat ) | ./level3`.
- **Référence commands.md :** commande dans `commands.md`, section Exploitation. Démo : `( python -c 'print "\x8c\x98\x04\x08" + "%60x%1$n"'; cat ) | ./level3`.

## 5. Exploitation logic
Format string : l’entrée est le format de printf. En mettant l’adresse de m au début du buffer, %1$n écrit le nombre d’octets imprimés (64) à cette adresse. Le test m == 64 passe → system("/bin/sh").

## 6. Reproducible procedure (for evaluation)
- **Commande :** `( python -c 'print "\x8c\x98\x04\x08" + "%60x%1$n"'; cat ) | ./level3` puis `cat /home/user/level4/.pass`.
- **Résultat attendu :** « Wait what?! » puis shell level4.
- **À dire :** « printf(buffer) donne une format string. Je mets l’adresse de m au début du buffer et j’utilise %60x%1$n pour écrire 64 à cette adresse. »

## 7. Oral defense points
- **Bug :** printf(buffer) avec buffer contrôlé par l’utilisateur (v(), après fgets).
- **GDB :** confirme que m est à 0x804988c et qu’après le payload elle vaut 64 ; %1$n écrit au 1er argument = début du buffer.
- **Payload :** 4 octets (adresse de m) + "%60x%1$n".
- **Fix :** printf("%s", buffer) ou ne jamais utiliser l’entrée comme format.

## 8. Common evaluator questions
- **Que fait %n ?** Il écrit le nombre d’octets déjà imprimés à l’adresse fournie par l’argument correspondant.
- **Pourquoi %1$n ?** Le 1er argument de printf est notre buffer ; en mettant une adresse au début, %1$n écrit à cette adresse.
- **Pourquoi 60 ?** 4 (adresse) + 60 = 64, valeur requise pour m.
- **Où est m ?** Variable globale en .bss à 0x804988c.
