# Décoder une ligne objdump

## Exemple

```bash
08048334 <_init>:
 8048334: 53              push   %ebx
 8048335: 83 ec 08        sub    $0x8,%esp
```

| Partie             | Exemple     | Explication                          |
| ------------------ | ----------- | ------------------------------------ |
| Adresse mémoire    | `8048334`   | Où l’instruction est en RAM         |
| Code machine (hex) | `53`        | Instruction brute en **hexadécimal** |
| Assembleur         | `push %ebx` | Traduction lisible                   |

## Chaîne de lecture

```
binaire (CPU) → hex (objdump) → assembleur (humain)
```

Exemple : `53` (hex) = `01010011` (binaire) → instruction `push %ebx`.

## Sections utiles

| Section | Rôle |
| --------|------|
| **.init** | Code exécuté au lancement du programme |
| **.plt**  | Sert à appeler des fonctions externes (printf, exit, etc.) — très important en exploitation |

Pour repérer les appels : `objdump -d level5 | grep call`

## Références
- `objdump(1)` : https://man7.org/linux/man-pages/man1/objdump.1.html
