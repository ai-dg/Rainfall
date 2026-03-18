# Backdoor (condition secrète)

## Concept
Une **backdoor** est une condition cachée dans le binaire : si l’entrée (ex. argument) prend une valeur précise, le programme exécute un comportement privilégié (ex. shell) au lieu du flux normal.

## Définition simple
- Pas d’overflow ni de corruption mémoire.
- Le code compare l’entrée à une **constante** (souvent en dur dans le binaire). Si égalité → branche « secrète » (ex. setresuid + execv("/bin/sh")).

## Où ça apparaît (level0)
- `main` appelle `atoi(argv[1])`, puis compare le résultat à une valeur en désassemblage : `cmp $0x1a7,%eax`.
- **0x1a7** = 423 en décimal. Si argv[1] = "423", la branche lance /bin/sh avec euid level1.

## Utilité
- Trouver la valeur : désassembler main (`objdump -d level0`), repérer la comparaison après atoi.

## Exemple level0
- Commande : `./level0 423`.
- Pas de payload binaire ; un seul argument entier.

## Résumé mental
Backdoor = valeur magique qui déclenche une branche cachée. Pas d’exploit mémoire.

## Références
- `atoi(3)` : https://man7.org/linux/man-pages/man3/atoi.3.html
