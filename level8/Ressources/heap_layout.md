# Layout heap et condition auth+0x20 (level8)

**Voir aussi :** `oob_read.md` pour la synthèse complète (out-of-bounds read, type d’attaque, chunk glibc, phrase examen).

## Concept
Le programme lit un **octet** à l’adresse **auth+0x20** (auth+32) pour décider si l’utilisateur est “authentifié”. Le bloc **auth** ne fait que 4 octets : auth+0x20 est **en dehors** du bloc auth → **lecture hors limites**. Une autre allocation (**service** = strdup) peut occuper cette zone ; en la contrôlant, on contrôle la valeur lue.

## Définition simple
- **auth** = pointeur vers un bloc malloc(4).
- **login** fait : si `*(auth+0x20) != 0` → `system("/bin/sh")`, sinon "Password:".
- On ne peut pas écrire 32 octets avec le seul strcpy(auth, ...) (limité à 30 et le bloc fait 4). Donc on n’écrase pas auth directement jusqu’à +0x20.
- En revanche, **auth+0x20** est une **adresse** dans le heap. Si le bloc **service** (strdup de notre entrée) est alloué juste après auth, cette adresse peut tomber **à l’intérieur** du buffer service.

## Schéma

```
  auth (malloc 4)
  +----+
  |....|  auth+0x00
  +----+
  |    |  ...
  +----+
  |????|  auth+0x20  ← login lit ici ; peut être dans le bloc service
  +----+
  service (strdup "service" + notre chaîne)
  +------------------+
  | "serviceAAAA..." |  ← si on met assez de 'A', auth+0x20 est ici
  +------------------+
```

## Où ça apparaît (level8)
- Commande **auth AAAA** → alloue auth (4 octets).
- Commande **service** + longue chaîne → strdup alloue un bloc (souvent adjacent à auth).
- Commande **login** → le programme lit *(auth+0x20). Si cette zone a été remplie par le buffer service (octet non nul), la condition est vraie → shell.

## Utilité en exploitation
- Pas d’écrasement d’adresse : on remplit une **zone** qui est interprétée comme “flag” d’authentification.
- La longueur de la chaîne après "service" détermine la taille du bloc et où tombent les octets ; **32** caractères (ou plus) suffisent souvent pour que auth+0x20 soit dans le bloc.

## Exemple
```
  auth AAAA
  service AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
  login
```
→ *(auth+0x20) = 0x41 (ou autre non nul) → shell.

## Résumé mental
- Bug = **lecture** hors limites (pas d’overflow d’écriture nécessaire).
- auth+0x20 tombe dans le chunk **service** ; en remplissant service avec des 'A', *(auth+0x20) = 0x41 → condition vraie.

## Références
- Glibc malloc internals (chunk headers / layout) : https://sourceware.org/glibc/wiki/MallocInternals
- `malloc(3)` : https://man7.org/linux/man-pages/man3/malloc.3.html
