# PLT (Procedure Linkage Table)

## Concept
La **PLT** est du **code** (une série de petits stubs) qui sert à appeler des fonctions externes (printf, exit, etc.). Très important en exploitation : chaque appel à une fonction dynamique passe par sa entrée PLT.

**Exemple** : `08048380 <printf@plt>` = « voici l’entrée pour appeler printf dans le binaire ».

## PLT vs GOT

| Élément | Nature                         |
| ------- | ------------------------------ |
| **PLT** | code (instructions assembleur) |
| **GOT** | données (table d’adresses)      |

- Le code appelle toujours la **même adresse** (ex. `printf@plt`).
- La première fois : le stub PLT appelle le linker, qui remplit la GOT.
- Les fois suivantes : le stub PLT fait `jmp *GOT[x]` vers la vraie fonction.

## Flux d’un appel

```
printf("hello")  en C
       ↓
main  →  call printf@plt
              ↓
         printf@plt  →  jmp *GOT[printf]
                              ↓
                         GOT[printf]  →  printf (libc)
```

Résumé : **printf → PLT → GOT → libc (printf réel)**. Si on modifie la GOT, on redirige l’appel.

## Où ça apparaît
- Section `.plt` du binaire.
- `objdump -d level5` : blocs du type :

```asm
  8048380 <printf@plt>:
    jmp    *0x8049824   ; saut indirect via GOT
    push   $0x0
    jmp    80482f0      ; résolution (premier appel)
```

Pour repérer tous les appels : `objdump -d level5 | grep call`.

## Utilité en exploitation (level5)
On ne modifie pas la PLT (c’est du code). On modifie la **GOT**. Au prochain `call exit@plt`, le CPU exécute le stub PLT qui fait `jmp *GOT[exit]` : si GOT[exit] = adresse de `o`, on exécute `o()`.

## Schéma

```
  .text          .plt              .got.plt
  -----          ----              --------
  call exit@plt  →  jmp *0x8049838  →  [0x8049838] = ???
                         ↑
                    on écrit ici l’adresse de o()
```

## Résumé mental
PLT = trampoline qui utilise la GOT. Exploit = modifier la GOT, pas la PLT.

## Références
- ELF (sections/relocations/GOT-PLT) : https://man7.org/linux/man-pages/man5/elf.5.html
- Dynamic linker (`ld.so`) : https://man7.org/linux/man-pages/man8/ld.so.8.html
