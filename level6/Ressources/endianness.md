# Endianness (little-endian)

## Concept
**Endianness** defines the byte order in memory for a multi-byte word. In **little-endian** (x86), the **low** byte is at the lowest address.

## Simple definition
- Address 0x08048454 stored in 4 bytes:
  - In memory (LE): `54 84 04 08` (low byte first).
  - In Python for a payload: `\x54\x84\x04\x08`. (`\x54` = one byte of value 0x54; allows writing raw bytes.)

## Where it appears (level6 and others)
- The address of `n` is **0x08048454**.
- We write it into the heap via strcpy: bytes must be in **little-endian** order so the CPU interprets it correctly at `call *ptr`.

## Table

| Value (hex)   | Bytes (LE) in memory | In Python        |
|---------------|----------------------|------------------|
| 0x08048454    | 54 84 04 08          | \x54\x84\x04\x08 |
| 0x8049838     | 38 98 04 08          | \x38\x98\x04\x08 |

## Use in exploitation
- Any payload that writes an address (GOT, function pointer, vptr, etc.) must use the **correct order** for the target architecture (i386 = LE).

## Level6 example
- Address of **n**: 0x08048454.
- Payload: `"A"*72 + "\x54\x84\x04\x08"` so the last 4 bytes form the value 0x08048454 when read in little-endian.

## Mental summary
Little-endian = low byte first. Addresses in payloads = always LE on x86.

## References
- `htonl(3)` / `ntohl(3)` (byte order and conversion): https://man7.org/linux/man-pages/man3/htonl.3.html
