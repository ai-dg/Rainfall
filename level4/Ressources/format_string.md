# Format string — writing a large value (level4)

## Concept
Same principle as level3: printf(buffer), we write to the address of **m** (0x8049810) the value **16930116** (0x1025544) so the program executes `/bin/cat .../.pass`.

## Where it appears (level4)
- **Buffer index**: found with "AAAA" + "%1$p.%2$p....%12$p" → the one that displays 0x41414141 is the index (often **12** on the official ISO).
- Payload: [4 bytes = 0x8049810] + "%16930112x" + "%12$n" (4 + 16930112 = 16930116).
- No need to keep stdin open (the program prints then exits).

## Mental summary
Format string with **index > 1** (buffer deeper on the stack). Same %n technique, padding to reach the target value.

## References
- `printf(3)` (%n, %k$): https://man7.org/linux/man-pages/man3/printf.3.html
