# Heap

## Concept
The **heap** is the memory region used for dynamic allocations (`malloc`, `strdup`, etc.). Blocks are contiguous in memory; an overflow in one block can overwrite the next.

## Simple definition
- `malloc(size)` returns a pointer to a block of size at least `size` (often more due to headers).
- Blocks are typically allocated next to each other. Exceeding a block's size **overwrites** the next block (or metadata).

## Diagram (simplified)

```
  low addr
  +------------------+
  | buffer (64 B)    |  ← strcpy fills here
  +------------------+
  | (header/padding) |  ← overflow continues
  +------------------+
  | ptr (4 B)        |  ← we overwrite here with address of n()
  +------------------+
  high addr
```

## Use in exploitation
- No return address on the stack to overwrite here: the target is the **function pointer** in the next block.
- On RainFall: **72** bytes (64 + 8) before reaching the 4 bytes of the pointer. We then write the address of `n` in little-endian.

## Mental summary
Heap = dynamically allocated blocks. Heap overflow = exceed one block and overwrite the next (here: function pointer).

**See also:** `heap_overflow_fp.md` for the full level6 synthesis (structure, flow, payload, GDB, fix).

## References
- Glibc malloc internals (chunk headers / ptmalloc): https://sourceware.org/glibc/wiki/MallocInternals
- `malloc(3)` (general allocation contract): https://man7.org/linux/man-pages/man3/malloc.3.html
