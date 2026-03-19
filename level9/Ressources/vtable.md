# Vtable et vptr (C++ — level9)

## Concept
En C++, les appels virtuels passent par une **table de fonctions** (vtable) pointée par un champ **vptr** dans l’objet. L’appel est `(*(obj->vptr)[index])(args)`. Si on contrôle **vptr** (overflow), on contrôle l’adresse appelée.

## Définition simple
- Chaque objet avec des méthodes virtuelles a un **vptr** (souvent à l’offset 0) qui pointe vers la vtable.
- La vtable est un tableau de pointeurs de fonctions. Premier appel virtuel = *(vptr+0).
- En asm : `mov eax, [obj]` (eax = vptr), `mov edx, [eax]` (edx = adresse à appeler), `call edx`.

## Où ça apparaît (level9)
- Deux objets **N** (0x6c octets chacun), alloués côte à côte. Premier : vptr à +0, annotation à +4. Second = premier+0x6c, son vptr à l’offset 0 du second.
- **setAnnotation(premier, argv[1])** : memcpy(premier+4, argv[1], strlen(argv[1])) **sans borne** → overflow vers le second objet.
- Offset pour atteindre le vptr du second : 4 (vptr premier) + 100 (annotation) + 4 (membre) = **108** octets.

## Schéma

```
  premier                    second
  +------+                   +------+
  | vptr |  +0               | vptr |  ← on écrase ici par premier+4
  +------+                   +------+
  | annot|  +4  ... overflow |
  +------+                   +------+
  ...
  Offset 108 = début du vptr du second
```

## Exploit
- On met **premier+4** dans second->vptr (derniers 4 octets du payload).
- À l’appel : *(second->vptr) = *(premier+4) = **les 4 premiers octets de notre payload** = adresse du shellcode (qu’on a mise là).
- Donc call saute vers le shellcode (ex. dans l’env).

## Résumé mental
vptr = pointeur vers la vtable. Overflow pour remplacer vptr par une adresse qu’on contrôle ; *(cette adresse) = adresse de la fonction appelée → on met l’adresse du shellcode.

**Voir aussi :** `concepts.md` pour la chaîne d’exploit complète, layout heap, GDB, payload.

## Références
- Itanium C++ ABI (vtable/vptr) : https://itanium-cxx-abi.github.io/cxx-abi/abi.html#vtable
