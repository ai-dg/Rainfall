# Endianness (little-endian)

## Concept
L’**endianness** définit l’ordre des octets en mémoire pour un mot multi-octets. En **little-endian** (x86), l’octet de **poids faible** est à l’adresse la plus basse.

## Définition simple
- Adresse 0x08048454 stockée sur 4 octets :
  - En mémoire (LE) : `54 84 04 08` (low byte first).
  - En Python pour un payload : `\x54\x84\x04\x08`. (`\x54` = un octet de valeur 0x54 ; permet d’écrire des octets bruts.)

## Où ça apparaît (level6 et autres)
- L’adresse de `n` est **0x08048454**.
- On l’écrit dans le heap via strcpy : les octets doivent être dans l’ordre **little-endian** pour que le CPU l’interprète correctement au `call *ptr`.

## Tableau

| Valeur (hex)   | Octets (LE) en mémoire | En Python        |
|---------------|------------------------|------------------|
| 0x08048454    | 54 84 04 08            | \x54\x84\x04\x08 |
| 0x8049838     | 38 98 04 08            | \x38\x98\x04\x08 |

## Utilité en exploitation
- Tout payload qui écrit une adresse (GOT, pointeur de fonction, vptr, etc.) doit utiliser le **bon ordre** pour l’architecture cible (i386 = LE).

## Exemple level6
- Adresse de **n** : 0x08048454.
- Payload : `"A"*72 + "\x54\x84\x04\x08"` pour que les 4 derniers octets forment la valeur 0x08048454 en lecture little-endian.

## Résumé mental
Little-endian = octet de poids faible en premier. Adresses dans les payloads = toujours en LE sur x86.

## Références
- `htonl(3)` / `ntohl(3)` (ordre d’octets et conversion) : https://man7.org/linux/man-pages/man3/htonl.3.html
