# Heap (tas)

## Concept
Le **heap** est la zone mémoire utilisée pour les allocations dynamiques (`malloc`, `strdup`, etc.). Les blocs sont contigus en mémoire ; un overflow dans un bloc peut écraser le suivant.

## Définition simple
- `malloc(size)` retourne un pointeur vers un bloc de taille au moins `size` (souvent plus à cause des en-têtes).
- Les blocs sont typiquement alloués côte à côte. Dépasser la taille d’un bloc **écrase** le bloc suivant (ou des métadonnées).

## Où ça apparaît (level6)
- `main` fait `malloc(0x40)` (buffer 64 octets) puis `malloc(4)` (pointeur de fonction).
- Layout typique : `[buffer 64 + en-tête/alignement][pointeur 4 octets]`.
- **strcpy(buffer, argv[1])** sans limite : en envoyant plus de 64 octets, on déborde vers le bloc du pointeur.

## Schéma (simplifié)

```
  low addr
  +------------------+
  | buffer (64 B)    |  ← strcpy remplit ici
  +------------------+
  | (en-tête/padding) |  ← overflow continue
  +------------------+
  | ptr (4 B)        |  ← on écrase ici par l’adresse de n()
  +------------------+
  high addr
```

## Utilité en exploitation
- Pas d’adresse de retour sur la stack à écraser ici : la cible est le **pointeur de fonction** dans le bloc suivant.
- Sur RainFall : **72** octets (64 + 8) avant d’atteindre les 4 octets du pointeur. On écrit ensuite l’adresse de `n` en little-endian.

## Exemple level6
- Avant : `ptr` pointe vers `m()` → affiche "Nope".
- Après overflow : `ptr` = adresse de `n()` → `call *ptr` exécute `n()` → `system("/bin/cat .../.pass")`.

## Résumé mental
Heap = blocs alloués dynamiquement. Overflow heap = dépasser un bloc et écraser le suivant (ici : pointeur de fonction).

**Voir aussi :** `heap_overflow_fp.md` pour la synthèse complète level6 (structure, flux, payload, GDB, fix).

## Références
- Glibc malloc internals (chunk headers / ptmalloc) : https://sourceware.org/glibc/wiki/MallocInternals
- `malloc(3)` (contrat général de l’allocation) : https://man7.org/linux/man-pages/man3/malloc.3.html
