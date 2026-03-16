# Level4 — Source reconstituée

Voir `source.c`.

## Logique

- **n()** lit une ligne, appelle **p(buffer)** qui fait **printf(buffer)** (format string).
- Variable globale **m** : si **m == 0x1025544**, le programme exécute **/bin/cat /home/user/level5/.pass** et affiche le mot de passe level5.

## Vulnérabilité

**Format string** : on écrit la valeur **0x1025544** (16930116) à l’adresse de **m** avec **%n**, ce qui déclenche l’appel à **system** et l’affichage du mot de passe.
