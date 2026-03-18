# Format string — écriture d’une grande valeur (level4)

## Concept
Même principe que level3 : printf(buffer), on écrit à l’adresse de **m** (0x8049810) la valeur **16930116** (0x1025544) pour que le programme exécute `/bin/cat .../.pass`.

## Où ça apparaît (level4)
- **Index du buffer** : trouvé avec "AAAA" + "%1$p.%2$p....%12$p" → celui qui affiche 0x41414141 est l’index (souvent **12** sur l’ISO).
- Payload : [4 octets = 0x8049810] + "%16930112x" + "%12$n" (4 + 16930112 = 16930116).
- Pas besoin de garder stdin ouvert (le programme affiche puis termine).

## Résumé mental
Format string avec **index > 1** (buffer plus profond sur la stack). Même technique %n, padding pour atteindre la valeur voulue.

## Références
- `printf(3)` (%n, %k$) : https://man7.org/linux/man-pages/man3/printf.3.html
