# Level9 — Walkthrough

## 1. Objectif

Obtenir un shell **bonus0** (dernier niveau Rainfall). Binaire C++, pas d’appel à **system** dans le binaire → **ret2libc** ou usage de la vtable.

## 2. Inspection

- Deux objets **N** alloués (0x6c octets chacun). **setAnnotation(premier, argv[1])** fait **memcpy(premier+4, argv[1], strlen(argv[1]))** sans borne → **overflow**.
- Ensuite appel virtuel sur le **second** objet : **(*(second->vptr))(second, first)**. En dépassant depuis le premier, on écrase **second->vptr**.

## 3. Vulnérabilité

- **Overflow** depuis le buffer d’annotation (100 octets) : on atteint le **vptr** du second objet (offset 104). En le remplaçant par **premier+4**, le programme exécute ***(premier+4)**. En mettant l’adresse de **system** à **premier+4**, on obtient **system(second)** ; il reste à faire en sorte que l’argument soit un pointeur vers "/bin/sh" (gadget ou disposition en mémoire).

## 4. Exploit

- Payload type : **[adresse system]** (4 B) + **padding** (100 B) + **[premier+4]** (vptr du second).
- Adresses **premier** et **system** à obtenir en **gdb** (heap, libc). Adapter selon la VM.

## 5. Récupération du mot de passe

Dans le shell bonus0 : `cat /home/user/bonus0/.pass`. Consigner dans `level9/flag`.
