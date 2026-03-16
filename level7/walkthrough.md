# Level7 — Walkthrough

## 1. Objectif

Afficher le mot de passe level8. Le programme ouvre `/home/user/level8/.pass`, le lit dans un buffer **c**, puis appelle **puts("~~")**. Il n’y a pas d’appel à **system**.

## 2. Inspection

- **main** alloue deux structures (chacune : champ + pointeur vers 8 octets). **strcpy(ptr1[1], argv[1])** et **strcpy(ptr2[1], argv[2])** sans limite. Puis fopen, fgets(c, …), puts(0x8048703).
- En dépassant 8 octets dans le premier strcpy, on écrase le pointeur **ptr2[1]** (destination du second strcpy).

## 3. Vulnérabilité

- **Arbitrary write** : on choisit la cible du second strcpy en écrasant ptr2[1]. On écrit donc argv[2] à l’adresse qu’on veut.

## 4. Exploit

- Écrire l’argument de puts (0x80485f4) provoque un `\0` à 0x80485f8 qui casse l’instruction **call** → segfault.
- **Contournement** : écraser la **GOT de puts** (0x8049928) avec l’adresse de **m** (0x80484f4). **m()** fait `printf(..., c, ...)` donc affiche **c** (où le mot de passe a été lu).
- **argv[1]** = 20 octets + "\x28\x99\x04\x08" (ptr2[1] = GOT puts).
- **argv[2]** = "\xf4\x84\x04\x08" (adresse de m).

## 5. Récupération du mot de passe

**m()** affiche `(mot de passe) - (timestamp)`. Consigner le mot de passe level8 dans `level7/flag`.
