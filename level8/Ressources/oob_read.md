# Level8 — Out-of-Bounds Read & Heap Layout Manipulation

## Objective

Exploit an **out-of-bounds read** on the heap by manipulating **memory layout**: the program reads at an address it shouldn't; that address falls in a region we control via another allocation.

## Main concept

Unlike previous levels:

- No address overwrite (no direct control flow like ret or GOT).
- No shellcode.
- No GOT overwrite.

Here: **we control what the program reads in memory**, not what it writes.

## Vulnerability (logical)

```c
auth = malloc(4);

if (*(auth + 0x20))
    system("/bin/sh");
```

- **auth** = 4 bytes allocated.
- The program reads **auth + 0x20** = **auth + 32** bytes.
- So read **outside** the auth buffer → **out-of-bounds read**.

## Heap organisation

**Contiguous** memory in chunks:

```
[ metadata ][ auth (4 bytes) ][ metadata ][ service (N bytes) ]
```

If **service** is allocated right after **auth**, then **auth + 0x20** can fall **inside** the service block.

## Attack idea

- `auth AAAA` → allocates auth (4 bytes).
- `service AAAA...` → allocates a block filled with non-zero characters.
- `login` → reads `*(auth + 0x20)`.

If auth+0x20 falls in service data, the value read is what we put (e.g. `'A'` = 0x41). So `*(auth+0x20) != 0` → condition true → shell.

## Result

```
*(auth + 0x20) = 0x41 ('A')
→ if (0x41 != 0) → TRUE → system("/bin/sh")
```

## Attack type

| Type                        | Level8 |
| --------------------------- |--------|
| Heap overflow               | No     |
| Function pointer overwrite  | No     |
| **Out-of-bounds read**      | Yes    |
| **Heap layout manipulation**| Yes    |
| Logic bug exploitation      | Yes    |

**Key concept:** the bug is not in **writing**, it's in **reading out of bounds**.

## Memory layout (glibc 32-bit)

Even with `malloc(4)`, the chunk has a **header** (metadata) and alignment:

| Element    | Size     |
| ---------- | -------- |
| Header     | 8 bytes  |
| Data (aligned) | 8 bytes  |
| Total chunk| 16 bytes |

```
[ prev_size ][ size ][ data (8 bytes) ]
                ↑
              auth points here (user data)
```

So `malloc(4)` doesn't use "4 bytes only" but an **aligned chunk**. Address **auth + 32** can therefore fall in the next chunk (service).

## Service allocation

```c
service = strdup(buf + 7);
```

- `strdup` does `malloc(strlen(...)+1)` then copies the string.
- New chunk: `[ header (8 bytes) ][ data ("AAAA...") ]`.

Typical global layout:

```
[ header auth ][ auth data ][ header service ][ service data ]
```

Example: auth = 0x1000 → auth+0x20 = 0x1020 can fall in **service data**.

## Exploit step by step

1. **auth AAAA** → allocate auth.
2. **service AAAA...** (32 characters or more) → allocate service with non-zero bytes.
3. **login** → the program reads `*(auth+0x20)`; this address falls in service → value read = 0x41 (or other non-zero) → condition true → shell.

## Why it works

- `*(auth+0x20)` reads **inside** the service zone (because it's contiguous to auth on the heap).
- We don't modify auth; we modify the **zone the program reads by mistake** by placing our service allocation there.

## Important conditions

- auth stays small (malloc(4)).
- service must be long enough for auth+0x20 to fall in its data.
- Avoid null bytes if the program stops on them (here 'A' is enough).

## Comparison with Level6

| Level | Attack type         | Mechanism                           |
| ----- | ------------------- | ----------------------------------- |
| 6     | Overwrite (write)   | Overflow → overwrite pointer        |
| 8     | Out-of-bounds read  | Read out of bounds → control value read |

## Simplified diagram

```
Heap:

[ auth (4 bytes) ][ ... ][ service ("AAAA....") ]
        |
        +---- auth + 0x20  ------> falls in service
```

## Mental summary

- The program **reads too far** (auth+32 when auth is only 4 bytes).
- That zone belongs to another allocation (service).
- We control that allocation (service contents).
- So we control the value read → login condition satisfied.

**TL;DR:** header = 8 bytes; malloc(4) ≈ 16 bytes real; auth+32 falls in service; exploit = control the **read**, not the write.

## Exam phrase

> The program reads at address auth+0x20 although auth is only 4 bytes. This read goes past the allocated block and lands in an adjacent heap region. By controlling that region via a service allocation, we force the value read to be non-zero and trigger shell execution.

## References

- Glibc malloc internals: https://sourceware.org/glibc/wiki/MallocInternals
- `strdup(3)`: https://man7.org/linux/man-pages/man3/strdup.3.html
