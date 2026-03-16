# Level2 — Walkthrough

## 1. Objectif

Obtenir un shell level3. Le binaire est setuid level3, sans fonction du type `system("/bin/sh")`.

## 2. Inspection

- **main** appelle **p()**.
- **p()** : buffer à `ebp-0x4c`, `gets(buffer)`, puis lecture de l’adresse de retour. Si `(ret & 0xb0000000) == 0xb0000000` → `printf("(%p)\n", ret)` et `_exit(1)`. Sinon `puts(buffer)`, `strdup(buffer)`, retour.

## 3. Vulnérabilité

- Buffer overflow via `gets()`.
- Contrainte : on ne peut pas mettre une adresse de type 0xb0... dans l’adresse de retour (sinon sortie immédiate). Donc pas de retour direct vers la stack.

## 4. Exploit

- Retourner vers un gadget **pop ; ret** (ex. 0x08048385) dans le binaire.
- Mettre ensuite **deux fois** l’adresse du buffer sur la stack : le `pop` consomme la première, le `ret` saute vers la deuxième (= buffer).
- Au début du buffer : **shellcode** execve("/bin/sh") (sans octets nuls ni `\n`).
- Offset : 80 octets jusqu’à l’adresse de retour.
- Adresse du buffer à estimer (ex. 0xbffff6c0 sur la VM sans ASLR).

## 5. Exécution

Voir la section Exploitation dans `commands.md`. Si l’adresse du buffer est incorrecte, essayer d’autres valeurs (0xbffff660, 0xbffff710, etc.).

## 6. Récupération du mot de passe

Dans le shell level3 : `cat /home/user/level3/.pass`, puis consigner dans `level2/flag`.
