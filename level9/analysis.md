# Level9 — Analyse technique

## Binaire

- C++ (level9.cpp), setuid **bonus0**. Pas de **system** ni "/bin/sh" dans le binaire → **ret2libc**.
- Imports : memcpy, strlen, _Znwj (operator new), _exit.

## Classe N (demanglée)

- **N(int)** : vptr à +0 (vtable 0x8048848), membre int à +0x68.
- **setAnnotation(char*)** : **memcpy(this+4, src, strlen(src))** sans limite → overflow.
- Vtable : operator+ (0x804873a), operator- (0x804874e).

## main

- argc &gt; 1 sinon exit(1).
- **malloc(0x6c)** → premier N(5), **malloc(0x6c)** → second N(6).
- **setAnnotation(premier, argv[1])** : copie argv[1] à partir de premier+4 → on peut dépasser et écrire dans le second objet.
- Appel virtuel : `(*(second->vptr))(second, first)` → on contrôle **second->vptr** via l’overflow.

## Layout

- Premier objet : [vptr 4][annotation 100 octets][int 4] = 0x6c octets. L’annotation va de +4 à +0x68.
- Second objet juste après (à premier+0x6c) : [vptr 4][…].
- Overflow : 104 octets (100 + 4 du int) pour atteindre le **vptr** du second. En écrivant **premier+4** dans ce vptr, l’appel lit ***(premier+4)** = adresse à mettre dans le payload (ex. **system**). L’appel devient **system(second)** ; il faut donc que **(second)** soit la chaîne **"/bin/sh"**.

## Problème

- Si on met vptr = premier+4 et *(premier+4) = system, on appelle **system(second)**. Pour que ça lance un shell, il faudrait que l’adresse **(second)** contienne "/bin/sh". Les premiers octets de **second** sont justement le vptr (premier+4), pas la chaîne.
- Solutions possibles : **ret2libc** avec **system** et adresse de "/bin/sh" (dans libc ou env), ou **gadget** qui fait system(second+4) si on met "/bin/sh" à second+4. Adresses à obtenir en **gdb** (heap, system, éventuellement gadget ou "/bin/sh").

## Exploit (schéma)

1. Trouver en gdb : adresse du **premier** objet (heap), **system** (libc), et si besoin "/bin/sh" ou un gadget.
2. Payload : **[system]** (4 B) + **padding** jusqu’à offset 104 + **[premier+4]** (nouveau vptr du second).
3. Pour que **system** reçoive "/bin/sh", il faut soit placer "/bin/sh" en début de second (alors vptr ne peut pas être premier+4), soit utiliser un gadget qui appelle system avec un argument lu depuis le payload (ex. premier+8 si "/bin/sh" y est).

## Adresses utiles

| Élément   | Valeur      |
|----------|-------------|
| Vtable N | 0x8048848   |
| operator+ | 0x804873a  |
| setAnnotation | 0x804870e |
