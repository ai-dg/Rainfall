# Endianness (little-endian) — level2

## Concept
Adresses en little-endian dans le payload : gadget, adresse du buffer.

## Lien avec level2
- Gadget 0x08048385 → `\x85\x83\x04\x08`.
- Buffer ex. 0xbffff6c0 → `\xc0\xf6\xff\xbf`.

## Références
- `htonl(3)` : https://man7.org/linux/man-pages/man3/htonl.3.html
