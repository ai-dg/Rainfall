# libc (C standard library)

## Concept
**libc** = C Library = C standard library. It provides core functions (I/O, strings, memory, process). Dynamic binaries reference it via GOT/PLT.

## Common functions (find with `readelf -s`, `ltrace`)

| Category   | Examples |
| ---------- | -------- |
| I/O, format | `printf`, `scanf`, `puts`, `sprintf` |
| Read       | `gets` ⚠️, `fgets`, `fopen`, `fread`, `fwrite` |
| Memory     | `malloc`, `free`, `calloc`, `realloc` |
| Strings    | `strlen`, `strcpy` ⚠️, `strncpy`, `strcmp`, `strcat` ⚠️ |
| Process    | `system` 💣, `exit`, `fork`, `execve` 💣 |

## In exploitation

- **⚠️ Vulnerable** (unbounded or format): `gets`, `strcpy`, `strcat`, `sprintf`, `printf(buffer)`.
- **💣 Targets:** `system("/bin/sh")`, `execve("/bin/sh", ...)` — often present or reachable via GOT overwrite / ret2libc.

In level5: no direct call to `system` in normal flow; function `o()` does `system("/bin/sh")`. We hijack **exit** (GOT) to **o** to run it.

## References
- `man 3 printf`, `man 3 strcpy`, etc.
- Glibc: https://www.gnu.org/software/libc/
