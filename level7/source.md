# Level7 — Source reconstituée

Voir `source.c`.

## Logique

- Deux paires (entier + pointeur vers buffer 8 octets). **strcpy** du premier argument dans le premier buffer, du second argument dans le second buffer, sans limite.
- En dépassant 8 octets dans le premier buffer, on écrase la structure suivante (entier + pointeur). Le pointeur est la **destination** du second strcpy : on peut donc écrire à une adresse arbitraire.
- Ensuite : ouverture de `/home/user/level8/.pass`, lecture dans **c**, puis **puts("~~")**. En modifiant l’argument de puts (dans le code) pour qu’il pointe vers **c**, puts affiche le mot de passe.

## Vulnérabilité

**Arbitrary write** via overflow + contrôle du pointeur de destination du second strcpy. Pas de **system** : on détourne l’argument de **puts** pour afficher le buffer **c**.
