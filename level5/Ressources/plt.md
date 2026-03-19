# PLT (Procedure Linkage Table)

## Concept
The **PLT** is **code** (a series of small stubs) used to call external functions (printf, exit, etc.). Very important in exploitation: every call to a dynamic function goes through its PLT entry.

**Example:** `08048380 <printf@plt>` = "here is the entry to call printf in the binary".

## PLT vs GOT

| Element | Nature                    |
| ------- | ------------------------- |
| **PLT** | code (assembly instructions) |
| **GOT** | data (address table)      |

- The code always calls the **same address** (e.g. `printf@plt`).
- First time: the PLT stub calls the linker, which fills the GOT.
- Subsequent times: the PLT stub does `jmp *GOT[x]` to the real function.

## Call flow

```
printf("hello")  in C
       ↓
main  →  call printf@plt
              ↓
         printf@plt  →  jmp *GOT[printf]
                              ↓
                         GOT[printf]  →  printf (libc)
```

Summary: **printf → PLT → GOT → libc (real printf)**. If we modify the GOT, we redirect the call.

## Where it appears
- Binary section `.plt`.
- `objdump -d level5`: blocks like:

```asm
  8048380 <printf@plt>:
    jmp    *0x8049824   ; indirect jump via GOT
    push   $0x0
    jmp    80482f0      ; resolution (first call)
```

To find all calls: `objdump -d level5 | grep call`.

## Use in exploitation (level5)
We do not modify the PLT (it's code). We modify the **GOT**. On the next `call exit@plt`, the CPU runs the PLT stub which does `jmp *GOT[exit]`: if GOT[exit] = address of `o`, we run `o()`.

## Diagram

```
  .text          .plt              .got.plt
  -----          ----              --------
  call exit@plt  →  jmp *0x8049838  →  [0x8049838] = ???
                         ↑
                    we write o()'s address here
```

## Mental summary
PLT = trampoline that uses the GOT. Exploit = modify the GOT, not the PLT.

## References
- ELF (sections/relocations/GOT-PLT): https://man7.org/linux/man-pages/man5/elf.5.html
- Dynamic linker (`ld.so`): https://man7.org/linux/man-pages/man8/ld.so.8.html
