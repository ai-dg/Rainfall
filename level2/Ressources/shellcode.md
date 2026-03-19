# Shellcode (level2)

## Concept
Machine code injected into the buffer (e.g. execve("/bin/sh")). Since the binary refuses a direct ret to the stack, we first return to a gadget that jumps to the buffer.

## Relation to level2
- Shellcode at the **start** of the payload; no NUL byte (gets stops at \n). Classic i386 execve("/bin/sh") ~25–30 bytes.
- Buffer address found in GDB (e.g. 0xbffff6c0); put twice after the gadget (for pop then ret).

## References
- `execve(2)`: https://man7.org/linux/man-pages/man2/execve.2.html
