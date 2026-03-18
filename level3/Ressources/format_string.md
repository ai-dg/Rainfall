# Format string — écriture en variable globale (level3)

## Concept
`printf(buffer)` avec buffer contrôlé → **format string**. On met l’adresse de la cible (variable globale `m`) au début du buffer ; `%k$n` écrit le nombre d’octets déjà imprimés à cette adresse.

## Où ça apparaît (level3)
- `v()` : fgets puis printf(buffer). Variable **m** @ 0x804988c ; si **m == 64** → system("/bin/sh").
- **Index** : le 1er argument de printf = notre buffer → **%1$n** écrit à l’adresse contenue au début du buffer.
- Payload : [4 octets = 0x804988c] + "%60x" + "%1$n" → total imprimé = 64 → m = 64.

## Résumé mental
Format string pour écrire une **valeur** (64) à une **adresse** (m). %1$n = écrire à l’argument 1 (notre buffer).

## Références
- `printf(3)` (%n) : https://man7.org/linux/man-pages/man3/printf.3.html
