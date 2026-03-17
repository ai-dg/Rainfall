# Bonus0 — Walkthrough

## 1. Objectif

Obtenir un shell (ou lire `/home/user/bonus1/.pass`) en exploitant le binaire **bonus0**, qui lit **deux lignes** sur stdin et les concatène dans un buffer de 42 octets.

## 2. Inspection

- Pas d’arguments : `./bonus0` puis deux lignes au clavier.
- `file`, `strings` : read, strcpy, strcat, strncpy → risque d’overflow.
- Désassemblage : `p()` lit 0x1000 octets puis strncpy 20 ; `pp()` fait strcpy + espace + strcat vers le buffer de `main` (42 octets).

## 3. Vulnérabilité

- **Overflow** : 20 + 2 + 20 = 42 octets + `\0` écrits dans un buffer de 42 octets → le null final dépasse et écrase la stack (saved EBP, puis adresse de retour).
- Pas de vérification de longueur dans strcpy/strcat. La 2ᵉ entrée (buf2) contrôle ce qui écrase la saved EIP.

## 4. Exploit (ret2env — méthode qui fonctionne sur la VM)

- **Idée** : le buffer ne permet que 20 octets utiles en 2ᵉ ligne ; on met un **shellcode** dans une variable d’environnement et on redirige EIP vers le nopsled.
- **Astuce 4095** : `read(0, buf, 0x1000)` lit jusqu’à 4096 octets. Si la 1ʳᵉ ligne = 4095 octets + `\n`, le premier `read()` consomme 4096 octets ; le second `read()` lit alors la 2ᵉ ligne (notre overflow).
- **Étapes** :
  1. Définir `PAYLOAD` avec nopsled + shellcode exéc `/bin/sh` (voir `commands.md`, section ret2env, pour la commande exacte).
  2. En GDB avec `env -i payload=$PAYLOAD ./bonus0` : `b main`, `r`, `x/500s environ` → noter une adresse dans le nopsled (ex. `0xbffffe57` → little-endian `\x57\xfe\xff\xbf`).
  3. Fichier d’exploit : 1ʳᵉ ligne 4095 octets + `\n`, 2ᵉ ligne = 9 octets + adresse nopsled (4 octets) + 7 octets + `\n`.
  4. Lancer : `cat /tmp/file - | env -i payload=$PAYLOAD ./bonus0`, puis `cat /home/user/bonus1/.pass`.

Détail des commandes dans `commands.md` (section « Alternative : ret2env »).

## 5. Récupération du flag

`cat /home/user/bonus1/.pass` dans le shell obtenu → noter dans `bonus0/flag`.
