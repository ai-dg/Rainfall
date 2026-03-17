# Bonus0 — Analyse technique

## Binaire

- **ELF 32-bit LSB**, i386, dynamiquement lié, non strippé.
- Imports : `read`, `puts`, `strcpy`, `strcat`, `strchr`, `strncpy`, `__libc_start_main`.

## Comportement

- **Aucun argument** : le programme lit tout depuis **stdin**.
- Affiche la chaîne `" - "` (rodata 0x80486a0), lit une ligne (jusqu’à 0x1000 octets), remplace `\n` par `\0`, copie **20 octets** (strncpy 0x14) dans un buffer.
- Répète une deuxième fois (deux buffers de 20 octets dans `pp`).
- Concatène : `strcpy(dest, buf1)` puis ajout d’un espace (2 octets en rodata 0x80486a4), puis `strcat(dest, buf2)`.
- `dest` est le buffer de **main** (42 octets : esp+0x16, frame 0x40).

## Vulnérabilité

- **strcpy** et **strcat** sans limite sur la taille de `dest`.
- On écrit **20 + 2 + 20 = 42 octets** + le `\0` final → le null est écrit **au-delà** du buffer de 42 octets → **overflow** (au moins 1 octet sur saved EBP).
- En envoyant **20 octets sans `\n`** sur la première ligne, buf1 n’a pas de `\0` dans les 20 premiers octets ; strncpy ne null-termine pas → on contrôle bien 20 octets. Idem pour la deuxième ligne.
- Selon le layout exact de la stack (alignement, padding), l’overflow peut atteindre **saved EBP (4)** et **adresse de retour (4)**. À confirmer en GDB (break à la fin de `pp`, inspecter la frame de `main`).

## Exploit

- **Ret2env (méthode qui fonctionne sur la VM Rainfall)** : le buffer ne contient que 20 octets utiles pour la 2ᵉ ligne ; on met un **shellcode** dans une variable d’environnement (`payload=...`) et on écrase l’adresse de retour par l’adresse du nopsled. Astuce **4095** : 1ʳᵉ ligne = 4095 octets + `\n` pour que le premier `read()` consomme exactement 4096 octets et que le second `read()` lise la 2ᵉ ligne. 2ᵉ ligne = 9 octets padding + adresse nopsled (little-endian) + 7 octets.
- **Ret2libc** (alternative, offset GDB souvent aberrant sur la VM) : écraser la ret par **system** avec **"/bin/sh"** en argument ; nécessite un offset fiable (sinon tester plusieurs paddings 7, 9, 10, 12).
- En GDB : pour ret2env, noter l’adresse du nopsled (`x/500s environ`) ; pour ret2libc, noter **system**, **"/bin/sh"** et l’offset.
