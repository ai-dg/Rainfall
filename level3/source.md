# Level3 — Source reconstituée

Voir `source.c`.

## Logique

- **v()** lit une ligne dans un buffer puis appelle **printf(buffer)**. L’entrée sert donc de chaîne de format.
- Une variable globale **m** est testée : si `m == 64`, le programme affiche "Wait what?!\n" et appelle **system("/bin/sh")**. Sinon il ne fait rien de plus.

## Vulnérabilité

**Format string** : en envoyant des spécificateurs (`%x`, `%n`, `%1$n`), on lit ou on écrit la stack. Pour gagner, on écrit la valeur **64** à l’adresse de **m** avec **%n** (écrit le nombre d’octets déjà imprimés). Payload : adresse de m (4 octets) + format produisant 60 caractères + **%1$n** → 64 écrit à m.
