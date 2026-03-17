# Bonus0 — Source reconstituée

Voir `source.c` (équivalent C du binaire).

## Logique

- **p(dest, prompt)** : affiche `" - "`, lit une ligne (read 0x1000), remplace `\n` par `\0`, copie 20 octets dans `dest` (strncpy).
- **pp(dest)** : appelle `p` deux fois (buf1, buf2), puis `strcpy(dest, buf1)`, ajoute un espace (2 octets), puis `strcat(dest, buf2)`.
- **main** : buffer 42 octets, appelle `pp(buffer)` puis `puts(buffer)`.

## Vulnérabilité

**Overflow** : on écrit 20+2+20 = 42 octets + `\0` dans un buffer de 42 octets. Le `\0` final est écrit après le buffer → corruption de la stack (saved EBP et adresse de retour). Sur la VM Rainfall, l’exploit qui fonctionne est **ret2env** : shellcode dans une variable d’environnement, EIP écrasé par l’adresse du nopsled ; astuce 4095 pour séparer les deux `read()`. Alternative : **ret2libc** (system + "/bin/sh") si l’offset en GDB est fiable.
