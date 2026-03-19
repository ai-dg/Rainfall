# Endianness (little-endian) — level2

## Concept
Addresses in little-endian in the payload: gadget, buffer address.

## Relation to level2
- Gadget 0x08048385 → `\x85\x83\x04\x08`.
- Buffer e.g. 0xbffff6c0 → `\xc0\xf6\xff\xbf`.

## References
- `htonl(3)`: https://man7.org/linux/man-pages/man3/htonl.3.html
