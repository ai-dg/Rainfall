# Level2 — Source reconstituée

Voir `source.c`.

## Logique

- **p()** : buffer 76 octets, `gets(buffer)`, lecture de l’adresse de retour (saved EIP). Si elle est dans la plage stack (0xb0000000–0xbfffffff), affichage et `_exit(1)`. Sinon `puts(buffer)` et `strdup(buffer)`.
- Aucun appel à `system` : il faut exécuter du shellcode.

## Vulnérabilité

Overflow via `gets()`. Le filtre interdit de retourner vers la stack, donc on retourne vers du code dans le binaire (gadget `pop; ret`) puis on fait sauter vers le buffer où se trouve le shellcode.
