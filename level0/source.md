# Level0 — Source reconstituée

Version simplifiée du programme vulnérable pour expliquer la vulnérabilité.

## Fichier

Voir `source.c` dans ce dossier.

## Logique

1. Le programme attend un argument : `argv[1]`.
2. Il le convertit en entier avec `atoi(argv[1])` et le compare à la constante **0x1a7** (423).
3. **Si égal :** il récupère l’euid/egid effectifs (level1 car binaire setuid), fixe les identités réelles avec `setresgid`/`setresuid`, puis lance `execv("/bin/sh", ["/bin/sh", NULL])`. Le shell hérite des privilèges level1.
4. **Sinon :** il écrit `"No !\n"` sur stderr et quitte avec le code 1.

## Vulnérabilité

Pas de corruption mémoire : une **condition secrète** (argument = 423) agit comme une backdoor. Quiconque découvre cette valeur (par analyse statique du binaire, ex. `objdump -d` et lecture de la comparaison `cmp $0x1a7,%eax`) peut obtenir un shell avec les droits du propriétaire du binaire (level1).

## Compilation (pour test local)

```bash
gcc -m32 -o level0_recon source.c
```

(Sur une machine 64 bits sans multilib, installer `gcc-multilib` ou compiler sur la VM / en 64 bits en enlevant `-m32` pour tester la logique.)

Sur une machine sans setuid, le shell obtenu avec `./level0_recon 423` restera celui de l’utilisateur courant. Sur la VM, le binaire est setuid level1, donc `./level0 423` donne un shell level1.
