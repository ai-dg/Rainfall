# Format string — writing to a global variable (level3)

## Concept
`printf(buffer)` with a controlled buffer → **format string**. We put the address of the target (global variable `m`) at the start of the buffer; `%k$n` writes the number of bytes already printed to that address.

## Where it appears (level3)
- `v()`: fgets then printf(buffer). Variable **m** @ 0x804988c; if **m == 64** → system("/bin/sh").
- **Index**: the 1st argument of printf = our buffer → **%1$n** writes to the address stored at the start of the buffer.
- Payload: [4 bytes = 0x804988c] + "%60x" + "%1$n" → total printed = 64 → m = 64.

## Mental summary
Format string to write a **value** (64) to an **address** (m). %1$n = write to argument 1 (our buffer).

## References
- `printf(3)` (%n): https://man7.org/linux/man-pages/man3/printf.3.html
