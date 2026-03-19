#!/usr/bin/env python3
"""Level0: backdoor — prints the command with the magic value (0x1a7 = 423)."""

# Value found by disassembling main: cmp $0x1a7,%eax
MAGIC = 0x1A7  # 423 in decimal

def main():
    cmd = f"./level0 {MAGIC}"
    print(cmd)
    print("# magic =", MAGIC, "(0x%x)" % MAGIC)

if __name__ == "__main__":
    main()
