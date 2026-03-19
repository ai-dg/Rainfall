# Level0 — Commands

## Connection

```bash
ssh level0@localhost -p 4242
```

Password: `level0`

---

## Recon

### Step 1 — Environment and binary

```bash
pwd
ls -la
```

**Goal:** Check the working directory and list the home files (including the level0 binary).

---

### Step 2 — Binary type and architecture

```bash
file level0
```

**Goal:** Confirm it is an ELF (Linux executable) and note the architecture (i386 / x86-64).

---

### Step 3 — Strings and hints

```bash
strings level0
```

**Goal:** Spot messages, paths, function names, or suspicious strings (e.g. gets, system, /bin/).

---

### Step 4 — ELF header and sections

```bash
readelf -h level0
```

**Goal:** Check the program entry point, ELF type, and architecture.

---

### Step 5 — Symbols (if not stripped)

```bash
readelf -s level0
# or if readelf -s shows nothing useful:
nm level0
```

**Goal:** List symbols (functions, variables) to identify exploitation targets (main, user functions, dangerous calls).

---

## What we expect to learn

- **Location and type:** The binary `level0` is in the home; it is an ELF (often i386 for Rainfall).
- **Strings:** Hints about the logic (prompts, paths, function names like `gets`, `system`, etc.).
- **Symbols:** Presence of `main`, user functions, and possibly risky calls (gets, strcpy, etc.) to guide the analysis.
- **No exploitation at this stage:** This is reconnaissance only for the next steps (dynamic analysis, vulnerability hypothesis).

---

---

## Executed results (recon)

**Step 1**
- `pwd` → `/home/user/level0`
- `ls -la`: binary `level0` present, **setuid level1** (`rwsr-x---+`), size 747441 bytes.

**Step 2 — file level0**
- setuid ELF 32-bit LSB executable, Intel 80386, **statically linked**, not stripped.

**Step 3 — strings**
- On the VM used, `strings` returned exit 126 (command absent or not executable). Do manually if available, or analyze the binary locally after copying.

**Step 4 — readelf -h**
- ELF32, Intel 80386, entry point `0x8048de8`, 5 program headers, 33 section headers.

**Step 5 — readelf -s**
- Binary not stripped, statically linked (many symbols). Notable:
  - `main` @ `0x08048ec0` (199 bytes)
  - `strcpy`, `execv`, `sscanf`, `printf`, `fprintf`, `fgets_unlocked`, etc.

---

---

## Binary extraction (local analysis)

From the host machine (where the project is cloned):

```bash
cd level0
sshpass -p 'level0' scp -o StrictHostKeyChecking=no -P 4242 level0@localhost:level0 ./level0.bin
```

**Goal:** Get a copy of the binary for local analysis (file, strings, readelf, objdump). The `level0.bin` file is git-ignored (do not version binaries).

---

## Local analysis (in ./level0)

```bash
file level0.bin
readelf -h level0.bin
strings level0.bin
readelf -s level0.bin | grep -E 'main|gets|system|exec|strcpy|scanf|printf|fgets'
objdump -d level0.bin | sed -n '/08048ec0 <main>/,/^[0-9a-f]* <[^>]*>:/p'
objdump -s -j .rodata level0.bin
```

**Results:** See `analysis.md`.

---

---

## Exploitation

### Step 6 — Run the binary with the magic argument

```bash
./level0 423
```

**Goal:** Pass the `atoi(argv[1]) == 0x1a7` check so the program executes `execv("/bin/sh", ...)` with euid level1. A level1 shell opens.

### Step 7 — Verify identity and retrieve the level1 password

In the obtained shell:

```bash
id
cat /etc/passwd
# or as indicated by the subject: file in the level1 home containing the password
ls -la /home/user/level1
cat /home/user/level1/.pass
```

**Goal:** Confirm we are level1 (`id`) and retrieve the password for `ssh level1@... -p 4242`.

### Step 8 — Connect as level1

```bash
exit
ssh level1@localhost -p 4242
```

**Goal:** Move to level1 with the retrieved password. Record the password in `level0/flag` (or in notes) for evaluation.

---

## Next investigation step

For the following levels: same approach (recon → binary analysis → hypothesis → exploitation → retrieve the next password).
