# Level4 — GDB disassembly (`p` + `n` + `main`)

Format: each instruction line is followed by a short **English** note (`--->`).

```bash
(gdb) disas p
Dump of assembler code for function p:
   0x08048444 <+0>:     push   %ebp               ---> Prologue.
   0x08048445 <+1>:     mov    %esp,%ebp          ---> Set up frame for p().
   0x08048447 <+3>:     sub    $0x18,%esp         ---> Allocate small stack area for outgoing args.
   0x0804844a <+6>:     mov    0x8(%ebp),%eax     ---> Load first argument (pointer) to p — user-controlled buffer.
   0x0804844d <+9>:     mov    %eax,(%esp)        ---> Pass it as the only argument to printf.
   0x08048450 <+12>:    call   0x8048340 <printf@plt>  ---> printf(buf) — **format string** (no fixed format).
   0x08048455 <+17>:    leave                     ---> Epilogue.
   0x08048456 <+18>:    ret                       ---> Return to n().
End of assembler dump.
(gdb) disas n
Dump of assembler code for function n:
   0x08048457 <+0>:     push   %ebp               ---> Prologue.
   0x08048458 <+1>:     mov    %esp,%ebp          ---> Frame for n().
   0x0804845a <+3>:     sub    $0x218,%esp        ---> Large frame for 0x200-byte buffer + locals.
   0x08048460 <+9>:     mov    0x8049804,%eax     ---> stdin (FILE*).
   0x08048465 <+14>:    mov    %eax,0x8(%esp)     ---> fgets 3rd arg: stdin.
   0x08048469 <+18>:    movl   $0x200,0x4(%esp)   ---> fgets size: 512 bytes.
   0x08048471 <+26>:    lea    -0x208(%ebp),%eax   ---> %eax = local buffer (ebp-0x208).
   0x08048477 <+32>:    mov    %eax,(%esp)        ---> fgets buffer pointer.
   0x0804847a <+35>:    call   0x8048350 <fgets@plt>  ---> fgets(buf, 0x200, stdin).
   0x0804847f <+40>:    lea    -0x208(%ebp),%eax   ---> %eax = same buffer.
   0x08048485 <+46>:    mov    %eax,(%esp)        ---> Argument to p().
   0x08048488 <+49>:    call   0x8048444 <p>      ---> p(buf) → printf with user format string.
   0x0804848d <+54>:    mov    0x8049810,%eax     ---> Load global m.
   0x08048492 <+59>:    cmp    $0x1025544,%eax    ---> Compare m to constant 0x01025544 (16930116).
   0x08048497 <+64>:    jne    0x80484a5 <n+78>    ---> If m != target, skip shell.
   0x08048499 <+66>:    movl   $0x8048590,(%esp)  ---> Put command string address (e.g. cat .pass) for system().
   0x080484a0 <+73>:    call   0x8048360 <system@plt>  ---> system(...) — win when m matches.
   0x080484a5 <+78>:    leave                     ---> Epilogue.
   0x080484a6 <+79>:    ret                       ---> Return to main.
End of assembler dump.
(gdb) disas main
Dump of assembler code for function main:
   0x080484a7 <+0>:     push   %ebp               ---> Prologue.
   0x080484a8 <+1>:     mov    %esp,%ebp          ---> Frame setup.
   0x080484aa <+3>:     and    $0xfffffff0,%esp   ---> Align stack.
   0x080484ad <+6>:     call   0x8048457 <n>      ---> main calls n() only.
   0x080484b2 <+11>:    leave                     ---> Epilogue.
   0x080484b3 <+12>:    ret                       ---> Return to libc.
End of assembler dump.
(gdb) 
```

**Global `m`** at **`0x08049810`** — overwritten via **`%n`** from the format string in **`p()`**.
