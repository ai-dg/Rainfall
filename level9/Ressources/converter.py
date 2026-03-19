#!/usr/bin/env python3
"""Convertit soit un entier en little endian (\\xXX x4), soit une chaîne hex en \\xXX..."""

import sys
import re

def main():
    if len(sys.argv) < 2:
        print("Usage: %s <valeur_32b|chaîne_hex>" % sys.argv[0], file=sys.stderr)
        print("  ex: %s 0xbffffc63  → \\x63\\xfc\\xff\\xbf" % sys.argv[0], file=sys.stderr)
        print("  ex: %s eb1f5e89... → \\xeb\\x1f\\x5e\\x89..." % sys.argv[0], file=sys.stderr)
        sys.exit(1)
    arg = sys.argv[1].strip().replace(" ", "").replace("\n", "")
    # Chaîne hex longue (sans 0x) → bytes en \xXX
    if len(arg) > 8 and re.match(r"^[0-9a-fA-F]+$", arg):
        if len(arg) % 2:
            arg = "0" + arg
        raw = bytes.fromhex(arg)
        out = "".join("\\x%02x" % b for b in raw)
        print(out)
        return
    # Une valeur 32 bits (décimal ou 0x...)
    val = int(arg, 0)
    if val < 0 or val > 0xFFFFFFFF:
        print("Erreur: valeur 32 bits attendue", file=sys.stderr)
        sys.exit(1)
    le = val.to_bytes(4, "little")
    out = "".join("\\x%02x" % b for b in le)
    print(out)

if __name__ == "__main__":
    main()
