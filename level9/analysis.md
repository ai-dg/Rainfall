# Level9 — Analyse technique

## Binaire

- C++ (level9.cpp), setuid **bonus0**. Pas d’appel à **system** ni chaîne "/bin/sh" dans le binaire.
- Imports : memcpy, strlen, _Znwj (operator new), _exit.

## Classe N (demanglée)

- **N(int)** : vptr à +0 (vtable 0x8048848), membre int à +0x68.
- **setAnnotation(char*)** : **memcpy(this+4, src, strlen(src))** sans limite → overflow.
- Vtable : operator+ (0x804873a), operator- (0x804874e).

## main

- argc > 1 sinon _exit(1).
- **operator new(0x6c)** → premier N(5), **operator new(0x6c)** → second N(6).
- **setAnnotation(premier, argv[1])** : copie argv[1] à partir de **premier+4** → on peut dépasser et écrire dans le second objet.
- Appel virtuel : `(*(second->vptr))(second, first)` → on contrôle **second->vptr** via l’overflow.

Séquence utile en GDB (main) :
- main+136 : mov eax, [esp+0x10] (eax = second)
- main+140 : mov eax, [eax] (eax = second->vptr)
- main+142 : mov edx, [eax] (edx = *vptr = cible du call)
- main+159 : call edx

## Layout

- Premier objet : [vptr 4][annotation 100][int 4] = 0x6c octets. L’annotation va de +4 à +0x68.
- Second objet juste après (premier+0x6c) : [vptr 4][…].
- **Overflow** : **108 octets** (4 + 100 + 4) pour atteindre et écraser le **vptr** du second. En mettant **premier+4** (ex. 0x0804a00c) dans ce vptr, l’appel lit ***(premier+4)** et saute à cette valeur.

## Solution retenue : shellcode dans l’environnement

- À **offset 0** (premier+4) : on met l’**adresse du shellcode** (nopsled + execve("/bin/sh") dans une variable d’env).
- À **offset 108** (second->vptr) : on met **premier+4**.
- Au moment du `call edx`, le programme exécute donc ***(premier+4)** = l’adresse lue à premier+4 = notre adresse env → exécution du shellcode → shell bonus0.

Pas besoin de ret2libc ni de gadget : on redirige le flux vers du code qu’on contrôle en env.

## Adresses utiles (exemple VM)

| Élément        | Valeur      |
|----------------|-------------|
| premier+4      | 0x0804a00c  |
| Vtable N       | 0x8048848   |
| setAnnotation  | 0x804870e   |

L’adresse du shellcode (nopsled dans `payload=...`) se trouve via `x/s environ` en GDB après `env -i payload=... ./level9`.
