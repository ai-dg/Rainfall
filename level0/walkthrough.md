# Level0 — Walkthrough

## 1. Objectif

Obtenir un shell avec les privilèges de l’utilisateur **level1** pour récupérer son mot de passe (ou le flag) et passer au level1.

## 2. Inspection du binaire

- **Setuid :** Le binaire appartient à level1 et a le bit setuid (`rwsr-x---`). En l’exécutant, l’euid devient level1.
- **Type :** ELF 32-bit i386, statiquement linké, non strié.
- **main** @ `0x08048ec0` : prend `argv[1]`, le convertit en entier (`atoi`), le compare à une constante, puis soit lance un shell, soit affiche un message.

## 3. Vulnérabilité identifiée

Il n’y a pas de buffer overflow. Le programme contient une **condition secrète** (backdoor) : si le premier argument, interprété comme entier, vaut **0x1a7** (423), il exécute `/bin/sh` après avoir fixé les identités réelles aux identités effectives (level1). Sinon il écrit `"No !\n"` sur stderr et quitte.

Découverte par analyse statique : dans le déassemblage de `main`, la comparaison `cmp $0x1a7,%eax` après `atoi` révèle la valeur attendue.

## 4. Raisonnement de l’exploit

1. Le binaire est setuid level1 → en l’exécutant, l’euid est déjà level1.
2. La branche « succès » fait `setresuid(euid, euid, euid)` et `setresgid(egid, egid, egid)` puis `execv("/bin/sh", ...)`.
3. Il suffit de fournir l’argument qui fait passer le test : **423** (ou 0x1a7).
4. Aucun payload ni corruption mémoire : un seul argument correct déclenche l’exécution du shell avec les droits level1.

## 5. Exécution de l’exploit

Sur la VM, après connexion en level0 :

```bash
./level0 423
```

Un shell s’ouvre ; le processus est alors en level1 (vérifiable avec `id`).

## 6. Récupération du mot de passe

Dans le shell level1 :

```bash
cat /etc/passwd
# ou
getent passwd level1
```

Le mot de passe de level1 est généralement dans un fichier dédié (ex. dans le home de level1) selon le déploiement Rainfall. Consulter ce fichier ou le sujet pour l’emplacement exact, puis se connecter en level1 :

```bash
exit
ssh level1@localhost -p 4242
```

Mot de passe : celui récupéré (à consigner dans `flag` ou dans les notes du level pour la suite).
