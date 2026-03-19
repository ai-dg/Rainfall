# Gadget (ROP / second jump)

## Concept
A **gadget** is a short instruction sequence already present in the binary (e.g. `pop reg; ret`). By placing this address as the return address, we "consume" words from the stack and then jump to the next address (which we control).

## Simple definition
- E.g. `pop ebx; ret`: pop reads 4 bytes (our buffer address), ret reads the next 4 (also the buffer address) and jumps → execution of code at the start of the buffer.

## Where it appears (level2)
- **0x08048385**: `pop ebx; ret`. Payload: [shellcode][padding][0x08048385][buf_addr][buf_addr]. At p's ret → gadget; after pop+ret → buffer (shellcode).

## Mental summary
Gadget = small existing piece of code to redirect flow (here: jump to the buffer despite the 0xb... constraint).

## References
- Finding gadgets: `objdump -d level2 | grep -A1 pop`
