# Bonus1 — Commandes

## Connexion

Se connecter comme **bonus1** (mot de passe = contenu de `bonus0/flag`) :

```bash
ssh bonus1@localhost -p 4242
```

---

## Recon

```bash
ls -la
file bonus1
./bonus1
```

Noter le comportement (arguments, stdin, sortie). Voir `analysis.md` pour l’analyse du binaire.

---

## Extraction du binaire (depuis l’hôte)

Dans le répertoire `bonus1/` :

```bash
sshpass -p "$(cat ../bonus0/flag)" scp -o StrictHostKeyChecking=no -P 4242 bonus1@localhost:bonus1 ./bonus1.bin
```

```bash
file bonus1.bin
strings bonus1.bin
objdump -d bonus1.bin | head -300
```

---

## GDB (sur la VM)

```bash
gdb -q ./bonus1
```

Repérer les appels (main, fonctions appelées), buffers, et l’offset jusqu’à la saved EIP si overflow.

---

## Exploitation

(À compléter après analyse : ret2libc, ret2env, format string, etc.)

---

## Récupération du flag

```bash
cat /home/user/bonus2/.pass
```

Noter le mot de passe dans `bonus1/flag`.
