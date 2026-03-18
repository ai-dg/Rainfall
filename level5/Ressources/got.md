# GOT (Global Offset Table)

## GOT overwrite attack (idée level5)
Si on peut **écrire en mémoire** (ex. format string `%n`), on remplace une entrée de la GOT par l’adresse d’une fonction de notre choix. Au prochain appel via la PLT, le programme saute vers cette fonction au lieu de la libc. En level5 : `exit(1)` devient en réalité `o()` → `system("/bin/sh")`.

## Concept
La **GOT** stocke des **pointeurs (adresses)** vers les fonctions externes (et parfois des variables globales externes).

- **Principalement** : adresses de fonctions (printf, puts, exit, etc.).
- **Parfois** : adresses de variables globales externes.

Le code du binaire ne connaît pas l’adresse de `exit` ou `printf` au moment du link. Au premier appel, le linker remplit la GOT ; les appels suivants font un **jump indirect** via cette entrée.

## Où ça apparaît
- Section `.got.plt` (ou `.got`) du binaire — en mémoire dans la zone **.data / .got** (voir schéma ci‑dessous).
- `readelf -r level5` → une entrée par fonction importée (exit, printf, …).
- Exemple level5 : **exit** → offset GOT `0x8049838`.

Exemple de contenu GOT (adresses réelles après résolution) :

| Adresse     | Contenu (valeur) | Symbole |
|------------|-------------------|---------|
| 0x0804981c | 0xf7e4c060        | printf  |
| 0x08049820 | 0xf7e3a210        | puts    |
| 0x08049824 | 0xf7e2d5b0        | exit    |

En C : `GOT[printf] = 0xf7e4c060` ; après overwrite (level5) : `GOT[exit] = adresse de o()`.

## Layout mémoire (rappel)

```
Adresse haute
┌───────────────┐
│ Stack (pile)  │  ← %esp (Stack Pointer)
│               │
├───────────────┤
│     Heap      │  ← malloc
├───────────────┤
│ .bss          │
│ .data         │
│ .got          │  ← GOT ici
│ .plt          │
├───────────────┤
│ Code (.text)  │
└───────────────┘
Adresse basse
```

**Stack** = zone pile ; **Stack Pointer (`%esp`)** = registre qui pointe vers le sommet de la pile.

## Utilité en exploitation
Si on contrôle une **écriture en mémoire** (ex. format string `%n`), on peut **remplacer** l’adresse dans la GOT par une autre (ex. une fonction du binaire). Au prochain appel, le programme saute vers notre cible.

| Cible      | Valeur écrite   | Effet                    |
|-----------|-----------------|--------------------------|
| GOT exit  | adresse de `o()`| `exit(1)` → `o()` → shell|

## Exemple concret (level5)
- Dans `n()` : `printf(buffer)` puis `exit(1)`.
- On écrase **GOT exit** (0x8049838) avec l’adresse de **o** (0x080484a4).
- Quand le programme fait `exit(1)` → en réalité le CPU lit GOT[exit] et saute vers **o()** → `system("/bin/sh")`.

En résumé : ce qui aurait dû être `exit("...")` devient `o()` → **BOOM** → shell.

## Schéma (flux)

```
  Avant exploit:
    call exit@plt  →  PLT  →  GOT[exit]  →  libc exit

  Après exploit:
    call exit@plt  →  PLT  →  GOT[exit]  →  o()  →  system("/bin/sh")
```

## Résumé mental
GOT = tableau d’adresses des fonctions externes. **GOT overwrite** = mettre une adresse de notre choix dans une entrée GOT pour détourner un appel de fonction.

## Références
- ELF : GOT/PLT et relocations (décrit aussi la structure générale) : https://man7.org/linux/man-pages/man5/elf.5.html
- Dynamic linker (résolution des symboles) : https://man7.org/linux/man-pages/man8/ld.so.8.html
