# Level8 — Source reconstituée

Voir `source.c`.

## Logique

- Boucle : affichage des adresses **auth** et **service**, lecture d’une ligne, comparaison avec **auth **, **reset**, **service**, **login**.
- **auth** : allocation de 4 octets, **strcpy** depuis l’entrée (longueur limitée à 30) → overflow.
- **login** : test ***(auth+0x20)** ; si non nul, **system("/bin/sh")**.

## Vulnérabilité

**auth** ne fait que 4 octets ; **auth+0x20** est en dehors de ce bloc. L’exploit repose sur le **layout du heap** : après **auth**, une allocation **service** (strdup) peut être contiguë ; **auth+0x20** tombe alors dans le buffer **service**. En passant une longue chaîne à **service**, on met un octet non nul à cet emplacement et **login** ouvre le shell.
