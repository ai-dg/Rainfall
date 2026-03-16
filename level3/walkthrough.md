# Level3 — Walkthrough

## 1. Objectif

Obtenir un shell level4. Le binaire est setuid level4 et appelle `system("/bin/sh")` si une condition est remplie.

## 2. Inspection

- **main** appelle **v()**.
- **v()** : `fgets(buffer, 512, stdin)` puis **printf(buffer)**. Ensuite lecture d’une variable globale **m** (adresse 0x804988c). Si `m == 64` (0x40) : `fwrite("Wait what?!\n", ...)` et **system("/bin/sh")**. Sinon, retour.

## 3. Vulnérabilité

- **Format string** : l’entrée est utilisée comme chaîne de format pour `printf`. On peut donc utiliser `%x`, `%n`, `%1$n`, etc.
- La variable `m` n’est jamais initialisée à 64 dans le code ; il faut l’écrire via l’exploit.

## 4. Exploit

- **%n** écrit le nombre d’octets déjà imprimés à l’adresse fournie par un argument.
- Le 1er argument de `printf` est l’adresse du buffer. Donc **%1$n** écrit à l’adresse lue dans le 1er argument, i.e. les 4 premiers octets du buffer si on y met une adresse.
- On met **0x804988c** (adresse de `m`) au début du buffer, puis un format qui affiche 60 caractères de plus (4 + 60 = 64) et **%1$n** → 64 est écrit à 0x804988c.
- Payload : `"\x8c\x98\x04\x08" + "%60x%1$n"`.

## 5. Exécution

Voir la section Exploitation dans `commands.md`. Garder stdin ouvert avec `( ... ; cat ) | ./level3` pour garder le shell.

## 6. Récupération du mot de passe

Dans le shell level4 : `cat /home/user/level4/.pass`, noter dans `level3/flag`.
