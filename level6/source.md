# Level6 — Source reconstituée

Voir `source.c`.

## Logique

- **main** alloue un buffer (64 octets) et un bloc de 4 octets servant de **pointeur de fonction**. Ce pointeur est initialisé avec l’adresse de **m**. Ensuite **strcpy(buffer, argv[1])** (sans contrôle de longueur), puis appel de la fonction pointée.
- **n()** exécute `system("/bin/cat /home/user/level7/.pass")` ; **m()** affiche "Nope".

## Vulnérabilité

**Buffer overflow** : en passant un argv[1] de plus de 64 octets, on écrase le pointeur de fonction. En le remplaçant par l’adresse de **n**, le programme exécute **n()** et affiche le mot de passe.
