# Endianness (little-endian) — level1

## Concept
Sur x86, les adresses sont stockées en **little-endian** : octet de poids faible en premier. L’adresse de retour écrasée doit être au bon format.

## Lien avec level1
- **run** = 0x08048444 → en payload : `\x44\x84\x04\x08` (4 octets en LE).

## Références
- `htonl(3)` / ordre d’octets : https://man7.org/linux/man-pages/man3/htonl.3.html
