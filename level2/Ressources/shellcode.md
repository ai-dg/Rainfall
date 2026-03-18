# Shellcode (level2)

## Concept
Code machine injecté dans le buffer (ex. execve("/bin/sh")). Comme le binaire refuse un ret direct vers la stack, on retourne d’abord vers un gadget qui saute au buffer.

## Lien avec level2
- Shellcode au **début** du payload ; sans octet NUL (gets s’arrête au \n). Classique i386 execve("/bin/sh") ~25–30 octets.
- Adresse du buffer trouvée en GDB (ex. 0xbffff6c0) ; à mettre deux fois après le gadget (pour pop puis ret).

## Références
- `execve(2)` : https://man7.org/linux/man-pages/man2/execve.2.html
