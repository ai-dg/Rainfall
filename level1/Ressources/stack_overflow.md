# Buffer overflow sur la stack (ret2win)

## Concept
Un **buffer overflow** sur la stack permet d’écraser les données situées après le buffer : saved EBP puis **adresse de retour**. En plaçant l’adresse d’une fonction cible (ex. `run` qui appelle system("/bin/sh")), le `ret` de la fonction vulnérable saute vers cette fonction au lieu de revenir à l’appelant.

## Définition simple
- `gets(buffer)` (ou lecture non bornée) remplit le buffer puis **déborde**.
- Les octets en trop écrasent saved EBP (4 octets) puis l’**adresse de retour** (4 octets). Au `ret`, le CPU charge cette adresse dans EIP → on contrôle le flux.

## Où ça apparaît (level1)
- `main` : buffer (64 octets à esp+0x10), puis `gets(buffer)`. Pas de borne → overflow.
- **Offset** jusqu’à l’adresse de retour : 76 octets sur RainFall (buffer + padding + saved EBP). Les 4 octets suivants = nouvelle adresse de retour.
- Cible : fonction **run** (0x08048444) qui fait system("/bin/sh").

## Schéma (stack)

```
  low addr   +------------------+
             | buffer (64 B)    |  ← gets() remplit ici
             +------------------+
             | padding / EBP    |
             +------------------+
             | saved EIP (ret) |  ← on écrit ici l’adresse de run
             +------------------+
  high addr
```

## Exploit
- Payload : 76 octets (padding) + adresse de `run` en little-endian (`\x44\x84\x04\x08`).
- Invocation : `( python -c 'print "A"*76 + "\x44\x84\x04\x08"'; cat ) | ./level1` pour garder stdin ouvert.

## Résumé mental
Overflow stack → écraser l’adresse de retour → au ret on saute vers une fonction du binaire (ret2win). Pas de shellcode.

## Références
- `gets(3)` (déprécié, non borné) : https://man7.org/linux/man-pages/man3/gets.3.html
