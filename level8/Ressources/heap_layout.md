# Heap layout and auth+0x20 condition (level8)

**See also:** `oob_read.md` for the full synthesis (out-of-bounds read, attack type, glibc chunk, exam phrase).

## Concept
The program reads one **byte** at address **auth+0x20** (auth+32) to decide if the user is "authenticated". The **auth** block is only 4 bytes: auth+0x20 is **outside** the auth block → **out-of-bounds read**. Another allocation (**service** = strdup) can occupy that region; by controlling it we control the value read.

## Simple definition
- **auth** = pointer to a malloc(4) block.
- **login** does: if `*(auth+0x20) != 0` → `system("/bin/sh")`, else "Password:".
- We can't write 32 bytes with strcpy(auth, ...) alone (limited to 30 and the block is 4 bytes). So we don't overwrite auth directly up to +0x20.
- However, **auth+0x20** is an **address** on the heap. If the **service** block (strdup of our input) is allocated right after auth, that address can fall **inside** the service buffer.

## Diagram

```
  auth (malloc 4)
  +----+
  |....|  auth+0x00
  +----+
  |    |  ...
  +----+
  |????|  auth+0x20  ← login reads here; may be inside service block
  +----+
  service (strdup "service" + our string)
  +------------------+
  | "serviceAAAA..." |  ← if we put enough 'A', auth+0x20 is here
  +------------------+
```

## Where it appears (level8)
- Command **auth AAAA** → allocates auth (4 bytes).
- Command **service** + long string → strdup allocates a block (often adjacent to auth).
- Command **login** → the program reads *(auth+0x20). If that zone was filled by the service buffer (non-zero byte), the condition is true → shell.

## Use in exploitation
- No address overwrite: we fill a **zone** that is interpreted as an authentication "flag".
- The length of the string after "service" determines block size and where bytes land; **32** characters (or more) often suffice for auth+0x20 to be in the block.

## Example
```
  auth AAAA
  service AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
  login
```
→ *(auth+0x20) = 0x41 (or other non-zero) → shell.

## Mental summary
- Bug = **read** out-of-bounds (no write overflow required).
- auth+0x20 falls in the **service** chunk; by filling service with 'A', *(auth+0x20) = 0x41 → condition true.

## References
- Glibc malloc internals (chunk headers / layout): https://sourceware.org/glibc/wiki/MallocInternals
- `malloc(3)`: https://man7.org/linux/man-pages/man3/malloc.3.html
