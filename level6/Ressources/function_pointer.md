# Pointeur de fonction

## Concept
Un **pointeur de fonction** est une variable qui contient l’adresse d’une fonction. L’appel se fait par **indirection** : `(*ptr)();` ou `ptr();` en C.

## Définition simple
- En C : `void (*fp)(void);` puis `fp = &ma_fonction;` et `fp();`.
- En asm : on charge la valeur du pointeur dans un registre, puis `call *%eax` (ou équivalent).

## Où ça apparaît (level6)
- Deux blocs sur le heap : buffer (64 octets) et un pointeur de 4 octets, initialisé avec l’adresse de **m**.
- Après `strcpy(buffer, argv[1])`, le code fait **call *ptr**.
- Si on écrase le pointeur (overflow) avec l’adresse de **n**, l’appel exécute `n()` au lieu de `m()`.

## Flux

```
  Normal :   ptr = &m   →  call *ptr  →  m()  →  "Nope"
  Exploit :  ptr = &n   →  call *ptr  →  n()  →  system("/bin/cat .../.pass")
```

## Utilité en exploitation
- La cible n’est pas une adresse de retour sur la stack mais **une seule valeur** : le contenu du pointeur.
- On n’a pas besoin de shellcode : on redirige vers une fonction déjà présente dans le binaire (`n`).

## Exemple (adresses level6)
- `m` = 0x08048468 (défaut)
- `n` = 0x08048454 (cible)
- Payload : 72 octets de padding + `\x54\x84\x04\x08` (adresse de n en little-endian).

## Résumé mental
Pointeur de fonction = adresse d’une fonction. Overflow pour écraser cette adresse → on choisit quelle fonction est appelée.

**Voir aussi :** `heap_overflow_fp.md` pour la synthèse level6 (flux normal vs exploit, comparaison avec level5, GDB).

## Références
- Function pointer (C) : https://en.cppreference.com/w/c/language/function_pointer
