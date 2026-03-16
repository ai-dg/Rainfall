# Level2 — Analyse technique

## Binaire

- ELF 32-bit i386, dynamically linked, setuid setgid level3.
- Imports : printf, fflush, gets, _exit, strdup, puts. **Pas de system.**

## Fonctions

- **main** (0x804853f) : appelle `p()` puis quitte.
- **p** (0x80484d4) :
  - `fflush(stdout)`
  - Buffer à `ebp-0x4c` (76 octets jusqu’à saved EBP)
  - `gets(buffer)` → overflow possible
  - Lit l’adresse de retour (saved EIP) : si `(ret & 0xb0000000) == 0xb0000000` → `printf("(%p)\n", ret)` et `_exit(1)`. Sinon : `puts(buffer)`, `strdup(buffer)`, `ret`.

## Vulnérabilité

- **Buffer overflow** via `gets()` dans `p()`.
- **Contrainte :** l’adresse de retour ne doit pas être dans la plage 0xb0000000–0xbfffffff (stack), sinon le programme quitte.
- Donc on ne peut pas retourner directement vers du shellcode sur la stack ; il faut retourner vers une adresse en .text (0x08...), puis rediriger vers le buffer.

## Exploit : gadget + shellcode

1. **Gadget** : `pop ebx; ret` à **0x08048385**. En y retournant : un `pop` consomme un mot, puis `ret` saute à l’adresse du mot suivant.
2. **Idée :** retour = gadget ; premier mot = adresse du buffer (consommé par le pop) ; deuxième mot = encore l’adresse du buffer (cible du `ret`). Ainsi le flux va au buffer (shellcode).
3. **Offset :** buffer à ebp-0x4c → 76 octets jusqu’à saved EBP, 4 pour EBP → **80 octets** jusqu’à l’adresse de retour.
4. **Payload :** `[shellcode + padding sur 80 octets][0x08048385][addr_buffer][addr_buffer]`. Adresse buffer typique (VM 32b, pas ASLR) : **0xbffff6c0** (sinon essayer 0xbffff660, 0xbffff710).

## Shellcode

Utiliser un shellcode x86 Linux execve("/bin/sh") sans octets nuls ni `\n` (ex. ~25–30 octets), au début du buffer.

## Adresses utiles

| Élément      | Valeur      |
|-------------|-------------|
| p           | 0x080484d4  |
| gadget pop; ret | 0x08048385 |
| buffer (estimation) | 0xbffff6c0 |
