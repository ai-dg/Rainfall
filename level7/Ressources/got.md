# GOT (Global Offset Table) — level7

**See also:** `heap_got_overwrite.md` for the level7 synthesis (heap overflow → arbitrary write → GOT overwrite, comparison with level5).

## Concept
The GOT holds the resolved addresses of external functions. In level7 we **replace** the **puts** entry with the address of **m** so that the call to `puts("~~")` actually runs `m()` and prints the buffer containing the password.

## Link with the level
- The program reads the password into buffer **c**, then calls **puts** (to print "~~").
- **m()** does `printf("%s - %d\n", c, time)`: prints exactly what we want (the password).
- We don't have a format string: we use an **arbitrary write** (overflow + second strcpy) to write the address of m into the puts GOT.

## Addresses (level7)
- GOT puts: **0x8049928** (write destination).
- m: **0x080484f4** (value to write).

## Flow

```
  Normal:  puts("~~")  →  PLT  →  GOT[puts]  →  libc puts
  Exploit: puts("~~")  →  PLT  →  GOT[puts]  →  m()  →  printf(c)  →  password
```

## Mental summary
Same idea as level5 (GOT overwrite), but the write primitive is different: arbitrary write via two strcpy instead of format string.

## References
- ELF: GOT/PLT and relocations: https://man7.org/linux/man-pages/man5/elf.5.html
