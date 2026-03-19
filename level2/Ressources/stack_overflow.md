# Buffer overflow with ret constraint (level2)

## Concept
Same idea as level1 (overflow via gets), but the binary **refuses** a return address in the range 0xb0000000–0xbfffffff (stack). A check of the form `(ret & 0xb0000000) == 0xb0000000` causes an exit if we return directly to the buffer (shellcode).

## Simple definition
- We cannot put the buffer address (0xb...) as the return address.
- **Solution:** return to a **gadget** in the binary (e.g. `pop; ret`). The gadget consumes one or two words from the stack; we put the buffer address there. The gadget's `ret` then jumps to the buffer → shellcode execution.

## Where it appears (level2)
- Function `p()`: gets(buffer), buffer at ebp-0x4c. **Offset** to ret = 80 bytes.
- Typical gadget: **0x08048385** (`pop ebx; ret`). By returning here: pop consumes the 1st word (buffer address), ret jumps to the 2nd word (also buffer address) → shellcode.

## Mental summary
Ret constraint → use a gadget in .text to make a second jump to the stack (buffer).

## References
- `gets(3)`: https://man7.org/linux/man-pages/man3/gets.3.html
