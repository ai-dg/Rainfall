#!/usr/bin/env python3
"""Level0: backdoor — affiche la commande avec la valeur magique (0x1a7 = 423)."""

# Valeur trouvée en désassemblant main : cmp $0x1a7,%eax
MAGIC = 0x1A7  # 423 en décimal

def main():
    cmd = f"./level0 {MAGIC}"
    print(cmd)
    print("# magic =", MAGIC, "(0x%x)" % MAGIC)

if __name__ == "__main__":
    main()
