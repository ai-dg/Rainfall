# Level4 — Walkthrough

## 1. Objectif

Obtenir le mot de passe level5. Le binaire est setuid level5 et peut exécuter **/bin/cat /home/user/level5/.pass** si une condition est remplie.

## 2. Inspection

- **main** appelle **n()**.
- **n()** : `fgets(buffer, 512, stdin)` puis **p(buffer)**. **p()** fait **printf(buffer)** → format string.
- Après **p(buffer)**, lecture de la variable globale **m** (0x8049810). Si **m == 0x1025544** (16930116) : **system("/bin/cat /home/user/level5/.pass")**. Le mot de passe s’affiche directement.

## 3. Vulnérabilité

- **Format string** : l’entrée sert de chaîne de format à **printf**. On écrit en mémoire avec **%n**.
- Il faut écrire **16930116** (0x1025544) à l’adresse **0x8049810**.

## 4. Exploit

- Adresse de **m** en little endian au début du buffer : `\x10\x98\x04\x08`.
- Puis **%16930112x** (4 + 16930112 = 16930116 octets imprimés) et **%k$n** (k = 1, 4 ou 7 selon la VM).
- La sortie est très volumineuse ; le mot de passe level5 est à la fin. Utiliser `| tail -1` pour ne garder que la dernière ligne.

## 5. Récupération du mot de passe

Consigner le mot de passe affiché dans `level4/flag`.
