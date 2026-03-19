# Endianness (little-endian) — level9

## Concept
On x86 (i386), addresses are stored in **little-endian**: low byte first. Payloads (argv[1], env) must follow this order.

## Link with level9
- **first+4** = 0x0804a00c → in payload: `\x0c\xa0\x04\x08` (last 4 bytes of argv[1] to overwrite second->vptr).
- **Shellcode address** (e.g. 0xbffffc63 in env) → in payload: `\x63\xfc\xff\xbf` (first 4 bytes of argv[1], read as *(first+4) at the call).

## Table

| Value (hex)   | level9 usage     | Bytes (LE)        |
|---------------|------------------|-------------------|
| 0x0804a00c    | first+4 (vptr)   | 0c a0 04 08       |
| 0xbffffc63    | shellcode (env)  | 63 fc ff bf       |

## Mental summary
All addresses in the payload (vptr, shellcode) in little-endian so the CPU interprets indirect calls correctly.

## References
- `htonl(3)` / `ntohl(3)` (byte order): https://man7.org/linux/man-pages/man3/htonl.3.html
