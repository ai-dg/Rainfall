# Level3 — Analyse technique

## Binaire

- ELF 32-bit i386, dynamically linked, setuid setgid level4.
- Imports : printf, fgets, fwrite, **system**.
- Variable globale **m** @ 0x804988c (symbole `m` dans .bss).

## Fonctions

- **main** (0x804851a) : appelle `v()`.
- **v** (0x80484a4) :
  - Buffer 512 octets à `ebp-0x208`, `fgets(buffer, 0x200, stdin)`.
  - **printf(buffer)** → chaîne de format contrôlée par l’entrée.
  - Lecture de la variable globale `m` (0x804988c). Si `m == 0x40` (64) : `fwrite("Wait what?!\n", ...)` puis **system("/bin/sh")** (chaîne à 0x804860d). Sinon : retour.

## Vulnérabilité

- **Format string** : l’entrée utilisateur est passée comme premier argument à `printf`, donc on peut utiliser des spécificateurs (`%x`, `%n`, `%1$n`, etc.).
- La variable `m` n’est jamais mise à 64 dans le flux normal ; il faut l’écrire via **%n** (écrit le nombre d’octets déjà imprimés à l’adresse fournie par un argument).

## Exploit

- **Cible :** écrire la valeur **0x40** (64) à l’adresse **0x804988c** (variable `m`).
- Le premier argument de `printf` est l’adresse du buffer (notre chaîne). Donc **%1$n** écrit à l’adresse contenue dans le 1er argument, i.e. au début du buffer si on y met une adresse.
- **Payload :** mettre **0x804988c** en little endian au début du buffer (4 octets), puis imprimer 60 caractères de plus (4 + 60 = 64) et utiliser **%1$n** pour écrire 64 à 0x804988c.
  - Format : `"\x8c\x98\x04\x08" + "%60x%1$n"`.

Après ce `printf`, `m == 64`, le test passe et `system("/bin/sh")` est exécuté.

## Adresses utiles

| Élément | Valeur      |
|--------|-------------|
| v      | 0x080484a4  |
| m      | 0x0804988c  |
| /bin/sh (appel system) | 0x804860d |
