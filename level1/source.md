# Level1 — Source reconstituée

Voir `source.c`.

## Logique

- **main** : buffer de 64 octets sur la stack, lu par `gets(buf)`. Aucune vérification de taille.
- **run** : affiche un message puis `system("/bin/sh")`. Jamais appelée par le code normal.

## Vulnérabilité

`gets()` lit jusqu’au premier `\n` ou EOF sans limite. Un entrée longue écrase la stack (saved EBP, adresse de retour). En plaçant l’adresse de `run` à la place de l’adresse de retour, on exécute `system("/bin/sh")` avec l’euid du propriétaire du binaire (level2).

Offset : 68 octets jusqu’à l’adresse de retour (buffer à esp+0x10, ret à esp+0x54).
