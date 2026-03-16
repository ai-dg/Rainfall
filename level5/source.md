# Level5 — Source reconstituée

Voir `source.c`.

## Logique

- **n()** lit une ligne, appelle **printf(buffer)** (format string), puis **exit(1)**. Le programme ne revient jamais de **n()**.
- **o()** fait **system("/bin/sh")** puis _exit(1). Elle n’est jamais appelée.

## Vulnérabilité

**Format string** : on peut écrire en mémoire avec **%n**. En remplaçant l’entrée **GOT** de **exit** par l’adresse de **o**, l’appel à **exit(1)** exécute **o()** et donne un shell.
