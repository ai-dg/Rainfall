# Level4 — Analyse technique

## Binaire

- ELF 32-bit i386, dynamically linked, setuid setgid level5.
- Imports : printf, fgets, **system**.
- Variable globale **m** @ 0x8049810.

## Fonctions

- **main** (0x80484a7) : appelle `n()`.
- **n** (0x8048457) : buffer 512 octets, `fgets(buffer, 0x200, stdin)`, puis **p(buffer)**.
- **p** (0x8048444) : **printf(argument)** → l’argument est notre buffer, donc **format string**.
- Après `p(buffer)`, lecture de **m** (0x8049810). Si **m == 0x1025544** (16930116) : **system("/bin/cat /home/user/level5/.pass")** (chaîne à 0x8048590). Sinon retour.

## Vulnérabilité

- **Format string** : l’entrée est passée à `p()` puis à `printf(buffer)`. On peut utiliser **%n** pour écrire en mémoire.
- Il faut écrire la valeur **0x1025544** (16930116) à l’adresse **0x8049810** (variable `m`).

## Exploit

- Même principe que level3 : adresse de `m` (4 octets) au début du buffer, puis format qui imprime **16930112** caractères de plus (4 + 16930112 = 16930116), puis **%k$n** (index à ajuster selon la VM, souvent 1, 4 ou 7).
- **Attention :** la sortie fait ~16 Mo (padding), la commande peut prendre quelques secondes.
- Une fois `m` écrit, le programme exécute **/bin/cat /home/user/level5/.pass** et affiche le mot de passe level5 directement (pas besoin de shell interactif).

## Adresses utiles

| Élément | Valeur      |
|--------|-------------|
| m      | 0x08049810  |
| Valeur à écrire | 0x1025544 (16930116) |
| Commande system | /bin/cat /home/user/level5/.pass |
