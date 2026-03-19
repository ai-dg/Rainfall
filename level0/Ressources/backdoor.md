# Backdoor (secret condition)

## Concept
A **backdoor** is a hidden condition in the binary: if the input (e.g. argument) takes a specific value, the program executes a privileged behavior (e.g. shell) instead of the normal flow.

## Simple definition
- No overflow or memory corruption.
- The code compares the input to a **constant** (often hardcoded in the binary). If equal → "secret" branch (e.g. setresuid + execv("/bin/sh")).

## Where it appears (level0)
- `main` calls `atoi(argv[1])`, then compares the result to a value visible in the disassembly: `cmp $0x1a7,%eax`.
- **0x1a7** = 423 in decimal. If argv[1] = "423", the branch launches /bin/sh with euid level1.

## How to find the value
- Disassemble main (`objdump -d level0`), locate the comparison after atoi.

## Example level0
- Command: `./level0 423`.
- No binary payload; a single integer argument.

## Mental summary
Backdoor = magic value that triggers a hidden branch. No memory exploit.

## References
- `atoi(3)`: https://man7.org/linux/man-pages/man3/atoi.3.html
