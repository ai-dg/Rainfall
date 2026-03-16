# Level0 — Analyse technique

## Binaire local

- **Fichier :** `level0.bin` (copie du binaire VM, non versionné).
- **Type :** ELF 32-bit LSB, i386, statically linked, not stripped.
- **Entry :** `0x8048de8`. **main :** `0x08048ec0` (199 octets).

## Logique de `main` (objdump)

1. **Argument :** `argv[1]` converti en entier via `atoi`.
2. **Comparaison :** `atoi(argv[1]) == 0x1a7` (423 en décimal).
3. **Si égal (423) :**
   - `strdup(0x80c5348)` → chaîne en .rodata = `"/bin/sh"`.
   - `getegid()` / `geteuid()` puis `setresgid` / `setresuid` (droits effectifs = level1).
   - `execv("/bin/sh", ["/bin/sh", NULL])` → lance un shell avec les privilèges level1.
4. **Si différent :** `fwrite` vers stderr (message type "No !" à l’adresse `0x80c5350`).

## Données .rodata pertinentes

- `0x80c5348` : `"/bin/sh"` (programme exécuté par `execv`).
- `0x80c5350` : message d’échec (ex. "No !\n" puis "FATAL: kernel too old" ou similaire).

## Hypothèse de vulnérabilité

Pas de buffer overflow : le programme attend un **seul argument numérique**. Si cet argument vaut **423** (0x1a7), il lance `/bin/sh` avec l’euid level1 (setuid). Sinon il affiche un message et quitte.

**Classe :** bypass par argument attendu (backdoor / condition secrète).

## Exploitation (raisonnement)

Sur la VM : `./level0 423` → le programme compare 423 à 0x1a7, égalité → `execv("/bin/sh", ...)` → shell en level1. Ensuite `cat /etc/passwd` ou `getent passwd level1` pour le mot de passe level1.

## Offsets / adresses utiles

| Élément    | Valeur      |
|-----------|-------------|
| main      | 0x08048ec0  |
| Constante | 0x1a7 (423) |
| /bin/sh   | 0x80c5348   |
