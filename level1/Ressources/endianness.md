# Endianness (little-endian) — level1

## Concept
On x86, addresses are stored in **little-endian**: least significant byte first. The overwritten return address must be in the correct format.

## Relation to level1
- **run** = 0x08048444 → in payload: `\x44\x84\x04\x08` (4 bytes in LE).

## References
- `htonl(3)` / byte order: https://man7.org/linux/man-pages/man3/htonl.3.html
