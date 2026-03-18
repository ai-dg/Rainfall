# Endianness (little-endian) — level9

## Concept
Sur x86 (i386), les adresses sont stockées en **little-endian** : octet de poids faible en premier. Les payloads (argv[1], env) doivent respecter cet ordre.

## Lien avec level9
- **premier+4** = 0x0804a00c → en payload : `\x0c\xa0\x04\x08` (derniers 4 octets de argv[1] pour écraser second->vptr).
- **Adresse shellcode** (ex. 0xbffffc63 dans l’env) → en payload : `\x63\xfc\xff\xbf` (4 premiers octets de argv[1], lus comme *(premier+4) au call).

## Tableau

| Valeur (hex)   | Usage level9      | Octets (LE)        |
|----------------|-------------------|--------------------|
| 0x0804a00c     | premier+4 (vptr)  | 0c a0 04 08        |
| 0xbffffc63     | shellcode (env)   | 63 fc ff bf        |

## Résumé mental
Toutes les adresses dans le payload (vptr, shellcode) en little-endian pour que le CPU interprète correctement les indirect calls.

## Références
- `htonl(3)` / `ntohl(3)` (ordre d’octets) : https://man7.org/linux/man-pages/man3/htonl.3.html
