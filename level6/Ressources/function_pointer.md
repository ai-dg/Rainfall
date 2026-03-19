# Function pointer

## Concept
A **function pointer** is a variable that holds the address of a function. The call is made by **indirection**: `(*ptr)();` or `ptr();` in C.

## Simple definition
- In C: `void (*fp)(void);` then `fp = &my_function;` and `fp();`.
- In asm: load the pointer value into a register, then `call *%eax` (or equivalent).

## Where it appears (level6)
- Two blocks on the heap: buffer (64 bytes) and a 4-byte pointer, initialised with the address of **m**.
- After `strcpy(buffer, argv[1])`, the code does **call *ptr**.
- If we overwrite the pointer (overflow) with the address of **n**, the call runs `n()` instead of `m()`.

## Flow

```
  Normal:   ptr = &m   →  call *ptr  →  m()  →  "Nope"
  Exploit:  ptr = &n   →  call *ptr  →  n()  →  system("/bin/cat .../.pass")
```

## Use in exploitation
- The target is not a return address on the stack but **a single value**: the pointer contents.
- We don't need shellcode: we redirect to a function already in the binary (`n`).

## Example (level6 addresses)
- `m` = 0x08048468 (default)
- `n` = 0x08048454 (target)
- Payload: 72 bytes padding + `\x54\x84\x04\x08` (address of n in little-endian).

## Mental summary
Function pointer = address of a function. Overflow to overwrite that address → we choose which function is called.

**See also:** `heap_overflow_fp.md` for the level6 synthesis (normal vs exploit flow, comparison with level5, GDB).

## References
- Function pointer (C): https://en.cppreference.com/w/c/language/function_pointer
