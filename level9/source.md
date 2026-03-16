# Level9 — Source reconstituée

Voir `source.c` (équivalent C simplifié).

## Logique

- Classe **N** : vtable à +0, buffer d’annotation à +4 (100 octets), int à +0x68.
- **setAnnotation** : **memcpy(this+4, src, strlen(src))** sans limite.
- **main** : deux objets N, **setAnnotation(premier, argv[1])**, puis appel de la fonction virtuelle sur le second avec (second, premier).

## Vulnérabilité

**Overflow** : en passant un **argv[1]** long, on dépasse le buffer du premier objet et on écrase le **vptr** du second. En mettant **premier+4** dans ce vptr et l’adresse de **system** à **premier+4**, l’appel devient **system(second)** ; il faut encore fournir un argument valide (pointeur vers "/bin/sh") via la disposition mémoire ou un gadget.
