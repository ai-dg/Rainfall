# GOT (Global Offset Table)

## GOT overwrite attack (level5 idea)
If we can **write to memory** (e.g. format string `%n`), we replace a GOT entry with the address of a function we choose. On the next call via the PLT, the program jumps to that function instead of libc. In level5: `exit(1)` effectively becomes `o()` → `system("/bin/sh")`.

## Concept
The **GOT** holds **pointers (addresses)** to external functions (and sometimes external global variables).

- **Mainly:** function addresses (printf, puts, exit, etc.).
- **Sometimes:** external global variable addresses.

The binary code does not know the address of `exit` or `printf` at link time. On first call, the linker fills the GOT; later calls do an **indirect jump** through that entry.

## Where it appears
- Binary section `.got.plt` (or `.got`) — in memory in the **.data / .got** region (see diagram below).
- `readelf -r level5` → one entry per imported function (exit, printf, …).
- Example level5: **exit** → GOT offset `0x8049838`.

Example GOT contents (real addresses after resolution):

| Address     | Content (value) | Symbol |
|------------|-----------------|--------|
| 0x0804981c | 0xf7e4c060      | printf |
| 0x08049820 | 0xf7e3a210      | puts   |
| 0x08049824 | 0xf7e2d5b0      | exit   |

In C: `GOT[printf] = 0xf7e4c060`; after overwrite (level5): `GOT[exit] = address of o()`.

## Memory layout (reminder)

```
High address
┌───────────────┐
│ Stack         │  ← %esp (Stack Pointer)
│               │
├───────────────┤
│     Heap      │  ← malloc
├───────────────┤
│ .bss          │
│ .data         │
│ .got          │  ← GOT here
│ .plt          │
├───────────────┤
│ Code (.text)  │
└───────────────┘
Low address
```

**Stack** = stack region; **Stack Pointer (`%esp`)** = register pointing to the top of the stack.

## Use in exploitation
If we control a **memory write** (e.g. format string `%n`), we can **replace** the address in the GOT with another (e.g. a function in the binary). On the next call, the program jumps to our target.

| Target    | Value written   | Effect                    |
|----------|------------------|---------------------------|
| GOT exit | address of `o()` | `exit(1)` → `o()` → shell |

## Concrete example (level5)
- In `n()`: `printf(buffer)` then `exit(1)`.
- We overwrite **GOT exit** (0x8049838) with the address of **o** (0x080484a4).
- When the program does `exit(1)` → the CPU actually reads GOT[exit] and jumps to **o()** → `system("/bin/sh")`.

In short: what would have been `exit("...")` becomes `o()` → **BOOM** → shell.

## Diagram (flow)

```
  Before exploit:
    call exit@plt  →  PLT  →  GOT[exit]  →  libc exit

  After exploit:
    call exit@plt  →  PLT  →  GOT[exit]  →  o()  →  system("/bin/sh")
```

## Mental summary
GOT = table of addresses of external functions. **GOT overwrite** = put an address of our choice in a GOT entry to hijack a function call.

## References
- ELF: GOT/PLT and relocations (also describes overall structure): https://man7.org/linux/man-pages/man5/elf.5.html
- Dynamic linker (symbol resolution): https://man7.org/linux/man-pages/man8/ld.so.8.html
