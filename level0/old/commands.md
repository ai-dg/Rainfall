# Level0 — Commandes

## Connection

```bash
ssh level0@localhost -p 4242
```

Mot de passe : `level0`

---

## Recon

### Étape 1 — Environnement et binaire

```bash
pwd
ls -la
```

**But :** Vérifier le répertoire de travail et lister les fichiers du home (dont le binaire level0).

---

### Étape 2 — Type et architecture du binaire

```bash
file level0
```

**But :** Confirmer qu’il s’agit d’un ELF (exécutable Linux) et noter l’architecture (i386 / x86-64).

---

### Étape 3 — Chaînes et indices

```bash
strings level0
```

**But :** Repérer des messages, chemins, noms de fonctions ou chaînes suspectes (ex. gets, system, /bin/).

---

### Étape 4 — En-tête et sections ELF

```bash
readelf -h level0
```

**But :** Vérifier l’entrée du programme, le type d’ELF et l’architecture.

---

### Étape 5 — Symboles (si non strié)

```bash
readelf -s level0
# ou si readelf -s ne montre rien d’utile :
nm level0
```

**But :** Lister les symboles (fonctions, variables) pour repérer des cibles d’exploitation (main, fonctions utilisateur, appels dangereux).

---

## What we expect to learn

- **Emplacement et type :** Le binaire `level0` est bien dans le home ; c’est un ELF (souvent i386 pour Rainfall).
- **Strings :** Indices sur la logique (prompts, chemins, noms de fonctions comme `gets`, `system`, etc.).
- **Symboles :** Présence de `main`, de fonctions utilisateur et éventuellement d’appels risqués (gets, strcpy, etc.) pour orienter l’analyse.
- **Pas d’exploitation à ce stade :** On ne fait que du repérage pour la suite (analyse dynamique, hypothèse de vulnérabilité).

---

---

## Résultats exécutés (recon)

**Étape 1**
- `pwd` → `/home/user/level0`
- `ls -la` : binaire `level0` présent, **setuid level1** (`rwsr-x---+`), taille 747441 octets.

**Étape 2 — file level0**
- setuid ELF 32-bit LSB executable, Intel 80386, **statically linked**, not stripped.

**Étape 3 — strings**
- Sur la VM utilisée, `strings` a retourné exit 126 (commande absente ou non exécutable). À faire manuellement si disponible, ou analyser le binaire en local après copie.

**Étape 4 — readelf -h**
- ELF32, Intel 80386, entry point `0x8048de8`, 5 program headers, 33 section headers.

**Étape 5 — readelf -s**
- Binaire non strié, statiquement linké (nombreux symboles). Notables :
  - `main` @ `0x08048ec0` (199 octets)
  - `strcpy`, `execv`, `sscanf`, `printf`, `fprintf`, `fgets_unlocked`, etc.

---

---

## Extraction du binaire (analyse locale)

Depuis la machine hôte (où le projet est cloné) :

```bash
cd level0
sshpass -p 'level0' scp -o StrictHostKeyChecking=no -P 4242 level0@localhost:level0 ./level0.bin
```

**But :** Récupérer une copie du binaire pour l’analyser en local (file, strings, readelf, objdump). Le fichier `level0.bin` est ignoré par git (ne pas versionner les binaires).

---

## Analyse locale (dans ./level0)

```bash
file level0.bin
readelf -h level0.bin
strings level0.bin
readelf -s level0.bin | grep -E 'main|gets|system|exec|strcpy|scanf|printf|fgets'
objdump -d level0.bin | sed -n '/08048ec0 <main>/,/^[0-9a-f]* <[^>]*>:/p'
objdump -s -j .rodata level0.bin
```

**Résultats :** Voir `analysis.md`.

---

---

## Exploitation

### Étape 6 — Lancer le binaire avec l’argument magique

```bash
./level0 423
```

**But :** Passer le test `atoi(argv[1]) == 0x1a7` pour que le programme exécute `execv("/bin/sh", ...)` avec l’euid level1. Un shell level1 s’ouvre.

### Étape 7 — Vérifier l’identité et récupérer le mot de passe level1

Dans le shell obtenu :

```bash
id
cat /etc/passwd
# ou selon le sujet : fichier dans le home level1 contenant le mot de passe
ls -la /home/user/level1
cat /home/user/level1/.pass
```

**But :** Confirmer qu’on est level1 (`id`) et récupérer le mot de passe pour `ssh level1@... -p 4242`.

### Étape 8 — Se connecter en level1

```bash
exit
ssh level1@localhost -p 4242
```

**But :** Passer au level1 avec le mot de passe récupéré. Consigner le mot de passe dans `level0/flag` (ou dans les notes) pour l’évaluation.

---

## Next investigation step

Pour les levels suivants : même démarche (recon → analyse du binaire → hypothèse → exploitation → récupération du mot de passe suivant).
