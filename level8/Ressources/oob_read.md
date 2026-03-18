# Level8 — Out-of-Bounds Read & Heap Layout Manipulation

## Objectif

Exploiter une **lecture hors limites (out-of-bounds read)** sur le heap en manipulant le **layout mémoire** : le programme lit à une adresse qu’il ne devrait pas ; cette adresse tombe dans une zone qu’on contrôle via une autre allocation.

## Concept principal

Contrairement aux niveaux précédents :

- Pas d’écrasement d’adresse (pas de control flow direct type ret ou GOT).
- Pas de shellcode.
- Pas de GOT overwrite.

Ici : **on contrôle ce que le programme lit en mémoire**, pas ce qu’il écrit.

## Vulnérabilité (logique)

```c
auth = malloc(4);

if (*(auth + 0x20))
    system("/bin/sh");
```

- **auth** = 4 octets alloués.
- Le programme lit **auth + 0x20** = **auth + 32** octets.
- Donc lecture **en dehors** du buffer auth → **out-of-bounds read**.

## Organisation du heap

Mémoire **contiguë** en chunks :

```
[ metadata ][ auth (4 bytes) ][ metadata ][ service (N bytes) ]
```

Si **service** est alloué juste après **auth**, alors **auth + 0x20** peut tomber **dans** le bloc service.

## Idée de l’attaque

- `auth AAAA` → alloue auth (4 octets).
- `service AAAA...` → alloue un bloc rempli de caractères non nuls.
- `login` → lit `*(auth + 0x20)`.

Si auth+0x20 tombe dans les données de service, la valeur lue est celle qu’on a mise (ex. `'A'` = 0x41). Donc `*(auth+0x20) != 0` → condition vraie → shell.

## Résultat

```
*(auth + 0x20) = 0x41 ('A')
→ if (0x41 != 0) → TRUE → system("/bin/sh")
```

## Type d’attaque

| Type                        | Level8 |
| --------------------------- |--------|
| Heap overflow               | Non    |
| Function pointer overwrite  | Non    |
| **Out-of-bounds read**      | Oui    |
| **Heap layout manipulation**| Oui    |
| Logic bug exploitation      | Oui    |

**Concept clé :** le bug n’est pas dans l’**écriture**, il est dans la **lecture hors limites**.

## Layout mémoire (glibc 32 bits)

Même avec `malloc(4)`, le chunk a un **header** (métadonnées) et un alignement :

| Élément    | Taille   |
| ---------- | -------- |
| Header     | 8 bytes  |
| Data (alignée) | 8 bytes  |
| Total chunk| 16 bytes |

```
[ prev_size ][ size ][ data (8 bytes) ]
                ↑
              auth pointe ici (données utilisateur)
```

Donc `malloc(4)` n’occupe pas “4 octets seuls” mais un **chunk aligné**. L’adresse **auth + 32** peut donc tomber dans le chunk suivant (service).

## Allocation service

```c
service = strdup(buf + 7);
```

- `strdup` fait `malloc(strlen(...)+1)` puis copie la chaîne.
- Nouveau chunk : `[ header (8 bytes) ][ data ("AAAA...") ]`.

Layout global typique :

```
[ header auth ][ auth data ][ header service ][ service data ]
```

Exemple : auth = 0x1000 → auth+0x20 = 0x1020 peut tomber dans **service data**.

## Exploit pas à pas

1. **auth AAAA** → alloue auth.
2. **service AAAA...** (32 caractères ou plus) → alloue service avec des octets non nuls.
3. **login** → le programme lit `*(auth+0x20)` ; cette adresse tombe dans service → valeur lue = 0x41 (ou autre non nul) → condition vraie → shell.

## Pourquoi ça marche

- `*(auth+0x20)` lit **dans** la zone service (car contiguë à auth sur le heap).
- On ne modifie pas auth ; on modifie la **zone que le programme lit par erreur** en y plaçant notre allocation service.

## Conditions importantes

- auth reste petit (malloc(4)).
- service doit être suffisamment long pour que auth+0x20 tombe dans ses données.
- Éviter les octets nuls si le programme s’arrête dessus (ici des 'A' suffisent).

## Comparaison avec Level6

| Level | Type d’attaque        | Mécanisme                    |
| ----- | --------------------- | ---------------------------- |
| 6     | Overwrite (écriture)  | Overflow → écraser pointeur  |
| 8     | Out-of-bounds read    | Lecture hors limites → contrôle de la valeur lue |

## Schéma simplifié

```
Heap :

[ auth (4 bytes) ][ ... ][ service ("AAAA....") ]
        |
        +---- auth + 0x20  ------> tombe dans service
```

## Résumé mental

- Le programme **lit trop loin** (auth+32 alors que auth ne fait que 4 octets).
- Cette zone appartient à une autre allocation (service).
- On contrôle cette allocation (contenu de service).
- Donc on contrôle la valeur lue → condition login satisfaite.

**TL;DR :** header = 8 bytes ; malloc(4) ≈ 16 bytes réel ; auth+32 tombe dans service ; exploit = contrôler la **lecture**, pas l’écriture.

## Phrase pour l’examen

> Le programme lit à l’adresse auth+0x20 alors que auth ne fait que 4 octets. Cette lecture dépasse le bloc alloué et tombe dans une zone adjacente du heap. En contrôlant cette zone via une allocation service, on force la valeur lue à être non nulle et on déclenche l’exécution du shell.

## Références

- Glibc malloc internals : https://sourceware.org/glibc/wiki/MallocInternals
- `strdup(3)` : https://man7.org/linux/man-pages/man3/strdup.3.html
