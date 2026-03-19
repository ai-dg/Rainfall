# Concepts — Rainfall

Référence rapide : types d’attaques, commandes de recon, registres et instructions (x86).

---

## Types d’attaques

| Attaque                        | Principe                     | Pattern à repérer (objdump / Ghidra)          | Objectif                           | Niveau importance |
| ------------------------------ | ---------------------------- | --------------------------------------------- | ---------------------------------- | ----------------- |
| **Buffer Overflow (stack)**    | Dépassement de buffer        | `gets`, `strcpy`, `scanf("%s")`, buffer local | Écraser `return address`           | ⭐⭐⭐⭐⭐             |
| **ret2libc**                   | Réutiliser libc              | appel indirect, pas de NX bypass nécessaire   | `system("/bin/sh")`                | ⭐⭐⭐⭐⭐             |
| **Format String**              | Contrôle du format `printf`  | `printf(user_input)`                          | Lire / écrire mémoire (`%x`, `%n`) | ⭐⭐⭐⭐⭐             |
| **GOT Overwrite**              | Modifier une entrée GOT      | écriture mémoire + appel PLT                  | Rediriger fonction (→ `system`)    | ⭐⭐⭐⭐              |
| **Function Pointer Overwrite** | Écraser pointeur de fonction | `void (*f)()` ou struct avec fonction         | Contrôler exécution                | ⭐⭐⭐               |
| **Heap Overflow**              | Corruption mémoire dynamique | `malloc` + écriture sans limite               | Modifier pointeurs                 | ⭐⭐                |
| **Command Injection**          | Injection commande système   | `system(user_input)`                          | Exécuter commandes                 | ⭐⭐                |
| **Auth Bypass / logique**      | Mauvaise vérification        | `strcmp`, conditions faibles                  | Bypass sécurité                    | ⭐⭐                |

---

## Commandes de recon

| Commande                   | But                 | Ce que tu cherches            | Exemple utile         |
| -------------------------- | ------------------- | ----------------------------- | --------------------- |
| `file level5`              | Type du binaire     | 32/64 bits, ELF, PIE          | `ELF 32-bit`          |
| `checksec level5`          | Protections         | NX, PIE, RELRO, Canary        | NX activé ?           |
| `strings level5`           | Chaînes lisibles    | `/bin/sh`, password, messages | `/bin/sh` 💣          |
| `objdump -d level5`        | Désassemblage       | fonctions, appels             | `call printf`         |
| `objdump -R level5`        | GOT                 | adresses fonctions dynamiques | `printf → 0x0804xxxx` |
| `readelf -s level5`        | Symboles            | noms de fonctions             | `system`, `main`      |
| `readelf -r level5`        | Relocations         | similaire GOT                 | entrées dynamiques    |
| `ltrace ./level5`          | appels libc         | `printf`, `system`            | flow runtime          |
| `strace ./level5`          | syscalls            | `execve`, `read`, `write`     | comportement système  |
| `gdb ./level5`             | debug               | stack, registres              | crash / RIP control   |
| `info functions` (gdb)     | fonctions           | voir `main`, etc.             | navigation            |
| `disas main` (gdb)         | code                | logique de `main`             | analyse rapide        |
| `x/s addr` (gdb)           | lire string         | vérifier `/bin/sh`            | mémoire               |
| `info proc mappings` (gdb) | mémoire             | libc base address             | ret2libc              |
| `nm level5`                | symboles (si debug) | fonctions visibles            | parfois vide          |
| `hexdump -C level5`        | vue brute           | structure binaire             | debug bas niveau      |

---

## Registres (x86)

| Registre | Rôle                                           |
| -------- | ---------------------------------------------- |
| `%eax`   | accumulateur (résultats, retours de fonctions) |
| `%ebx`   | registre général                               |
| `%ecx`   | compteur (boucles)                             |
| `%edx`   | données supplémentaires                        |
| `%esp`   | stack pointer ⚠️                               |
| `%ebp`   | base pointer (frame stack)                     |
| `%eip`   | instruction pointer (où on est dans le code)   |

---

## Instructions stack (x86)

| Instruction | Action principale | Effet sur `%esp` | Ce qui se passe en mémoire (stack) | Équivalent simplifié                          |
| ----------- | ----------------- | ---------------- | ---------------------------------- | --------------------------------------------- |
| `push X`    | empile une valeur | `%esp -= 4`      | écrit `X` à l'adresse `%esp`       | `esp = esp - 4; *esp = X;`                    |
| `pop X`     | dépile une valeur | `%esp += 4`      | lit valeur depuis `%esp` vers `X`  | `X = *esp; esp = esp + 4;`                    |
| `call addr` | appel de fonction | `%esp -= 4`      | push l'adresse de retour           | `push return_addr; jmp addr;`                 |
| `jmp addr`  | saut inconditionnel | aucun effet     | aucun accès stack                  | `goto addr;`                                  |
| `jmp *addr` | saut indirect (via mémoire) | aucun effet | lit une adresse en mémoire puis saute | `goto *(addr);` (ex: GOT)                     |
| `sub X, %esp` | réserve de la place sur la stack | `%esp -= X` | crée un espace pour variables locales | `esp = esp - X;`                              |
| `mov src, dst` | copie une valeur | aucun effet direct | copie une donnée (registre/mémoire) | `dst = src;`                                  |
| `lea addr, reg` | charge une adresse (pas la valeur) | aucun effet | aucune écriture mémoire | `reg = &addr;`                                |