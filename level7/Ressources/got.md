# GOT (Global Offset Table) — level7

## Concept
La GOT stocke les adresses résolues des fonctions externes. En level7, on **remplace** l’entrée de **puts** par l’adresse de **m** pour que l’appel à `puts("~~")` exécute en réalité `m()` et affiche le buffer contenant le mot de passe.

## Lien avec le level
- Le programme lit le mot de passe dans un buffer **c**, puis appelle **puts** (pour afficher "~~").
- **m()** fait `printf("%s - %d\n", c, time)` : affiche exactement ce qu’on veut (le mot de passe).
- On n’a pas de format string : on utilise une **arbitrary write** (overflow + second strcpy) pour écrire l’adresse de m dans la GOT de puts.

## Adresses (level7)
- GOT puts : **0x8049928** (destination de l’écriture).
- m : **0x080484f4** (valeur à écrire).

## Flux

```
  Normal :  puts("~~")  →  PLT  →  GOT[puts]  →  libc puts
  Exploit : puts("~~")  →  PLT  →  GOT[puts]  →  m()  →  printf(c)  →  mot de passe
```

## Résumé mental
Même idée que level5 (GOT overwrite), mais la primitive d’écriture est différente : arbitrary write via deux strcpy au lieu de format string.

## Références
- ELF : GOT/PLT et relocations : https://man7.org/linux/man-pages/man5/elf.5.html
