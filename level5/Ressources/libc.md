# libc (bibliothèque C standard)

## Concept
**libc** = Library C = bibliothèque C standard. Elle fournit les fonctions de base (E/S, chaînes, mémoire, processus). Les binaires dynamiques y font référence via la GOT/PLT.

## Fonctions courantes (repérer avec `readelf -s`, `ltrace`)

| Catégorie | Exemples |
| --------- | -------- |
| E/S, format | `printf`, `scanf`, `puts`, `sprintf` |
| Lecture | `gets` ⚠️, `fgets`, `fopen`, `fread`, `fwrite` |
| Mémoire | `malloc`, `free`, `calloc`, `realloc` |
| Chaînes | `strlen`, `strcpy` ⚠️, `strncpy`, `strcmp`, `strcat` ⚠️ |
| Processus | `system` 💣, `exit`, `fork`, `execve` 💣 |

## En exploitation

- **⚠️ Vulnérables** (sans borne ou format) : `gets`, `strcpy`, `strcat`, `sprintf`, `printf(buffer)`.
- **💣 Cibles** : `system("/bin/sh")`, `execve("/bin/sh", ...)` — souvent présentes ou atteignables via GOT overwrite / ret2libc.

En level5 : pas d’appel direct à `system` dans le flux normal ; la fonction `o()` fait `system("/bin/sh")`. On détourne **exit** (GOT) vers **o** pour l’exécuter.

## Références
- `man 3 printf`, `man 3 strcpy`, etc.
- Glibc : https://www.gnu.org/software/libc/
