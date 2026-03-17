# Level9 — Source reconstituée

Voir `source.c` (équivalent C simplifié).

## Logique

- Classe **N** : vtable à +0, buffer d’annotation à +4 (100 octets), int à +0x68.
- **setAnnotation** : **memcpy(this+4, src, strlen(src))** sans limite.
- **main** : deux N, **setAnnotation(premier, argv[1])**, puis **(*(second->vptr))(second, first)**.

## Vulnérabilité

**Overflow** : un **argv[1]** long dépasse le buffer du premier et écrase le **vptr** du second (offset **108**). En mettant **premier+4** dans ce vptr, l’appel exécute ***(premier+4)**. En plaçant à **premier+4** l’adresse d’un shellcode (ex. en variable d’environnement), on exécute ce shellcode → shell bonus0.
