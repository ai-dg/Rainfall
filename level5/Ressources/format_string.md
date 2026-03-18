# Format string (chaîne de format)

## Concept
Quand l’entrée utilisateur est passée comme **premier argument** à `printf` (au lieu d’une chaîne fixe), l’utilisateur contrôle la **chaîne de format** et peut lire/écrire la stack et la mémoire.

## Définition simple
- `printf(format, arg1, arg2, ...)` : `format` indique comment afficher les arguments.
- Si `format` vient de l’utilisateur (ex. `printf(buffer)`), les **spécificateurs** (`%d`, `%p`, `%n`, etc.) sont interprétés.
- **%n** : écrit le **nombre d’octets déjà imprimés** à l’adresse pointée par l’argument correspondant.

## Où ça apparaît (level5)
Dans `n()` : `printf(buffer);` — pas de chaîne fixe, donc `buffer` est la chaîne de format. On envoie par exemple `"AAAA%4$p"` pour tester.

## Primitives utiles

| Spécificateur | Effet |
|---------------|--------|
| %k$p | Affiche le kᵉ argument comme pointeur (lecture stack) |
| %k$n | Écrit le nombre d’octets imprimés à l’adresse dans le kᵉ argument |
| %nx  | Affiche un entier en hex sur n caractères (padding) |

## Pourquoi c’est utile
- **Lecture** : trouver l’**index** du buffer sur la stack (envoyer `AAAA` + `%1$p.%2$p.%3$p.%4$p` → celui qui affiche `0x41414141` est notre buffer).
- **Écriture** : mettre l’adresse GOT au début du buffer, puis `%padding x%k$n` pour écrire la valeur voulue à cette adresse.

## Exemple concret (level5)
1. Payload test : `"AAAA" + "%1$p.%2$p.%3$p.%4$p.%5$p"` → sortie `...0x41414141...` → index **4**.
2. Exploit : buffer = [adresse GOT exit en 4 octets] + `"%134513824x%4$n"`.
   - Total octets imprimés avant `%4$n` = 4 + 134513824 = 0x080484a4 (adresse de `o`).
   - `%4$n` écrit ce nombre à l’adresse lue dans l’argument 4 = notre buffer = 0x8049838 (GOT exit).

## Schéma (stack au moment de printf)

```
  esp+0   →  adresse de notre buffer (argument 1 = format)
  esp+4   →  ...
  esp+8   →  ...
  esp+12  →  ...   ← argument 4 = pointeur vers notre buffer (contient GOT exit)
  ...
  %4$n écrit à *(arg4) = *0x8049838
```

## Résumé mental
Format string = contrôler le premier argument de `printf`. %k$p pour lire, %k$n pour écrire à une adresse qu’on place dans le buffer (index k).

## Références
- `printf(3)` (rôle de `%n`) : https://man7.org/linux/man-pages/man3/printf.3.html
