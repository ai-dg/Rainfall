# Arbitrary write

**See also:** `heap_got_overwrite.md` for the level7 synthesis (heap layout, exploit chain, GDB, exam phrase).

## Concept
An **arbitrary write** lets us write a **value** to an **address** we choose. Here we get it by controlling the **destination** of the second `strcpy` via a first overflow (heap).

## Simple definition
- First `strcpy(dest1, argv[1])`: no bound, we can exceed `dest1` and overwrite other variables (e.g. `dest2`).
- If `dest2` is used as the **destination** of the second `strcpy(dest2, argv[2])`, then we choose **where** argv[2] is copied: we put the target address in argv[1], the value in argv[2].

## Where it appears (level7)
- Two structures: ptr1 (8-byte block), ptr2 (8-byte block). Each has a pointer field to a buffer.
- `strcpy(ptr1[1], argv[1])` then `strcpy(ptr2[1], argv[2])`.
- By overflowing the first buffer we overwrite **ptr2[1]** (the 2nd strcpy destination).
- We put **GOT of puts** in argv[1] (at the offset that overwrites ptr2[1]), and **address of m** in argv[2] → the 2nd strcpy writes the address of m into the GOT.

## Diagram

```
  argv[1] = [padding 20 bytes][puts GOT address]
              ↓ overflow
  ptr1[1] fills its block, then overwrites ptr2[0], ptr2[1]
  ptr2[1] = puts GOT address  →  strcpy(GOT_puts, argv[2])
  argv[2] = address of m (4 bytes)  →  write to GOT puts
```

## Use in exploitation
- One "gadget": **write a value to a chosen address**.
- Target = GOT entry (puts); value = address of the function we want to call instead (m).

## Level7 example
- Offset to ptr2[1]: **20** bytes (8 + 8 + 4 depending on layout).
- argv[1] = `"A"*20 + "\x28\x99\x04\x08"` (GOT puts 0x8049928).
- argv[2] = `"\xf4\x84\x04\x08"` (m = 0x080484f4).
- Result: `puts("~~")` calls m() which prints the buffer containing the password.

## Mental summary
Arbitrary write = control both the write address and the value. Here: overflow to control the 2nd strcpy destination, then write to the GOT.

## References
- `strcpy(3)` (no bound / copy until `\0`): https://man7.org/linux/man-pages/man3/strcpy.3.html
