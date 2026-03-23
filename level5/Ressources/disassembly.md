# Level5 — GDB disassembly (`o` + `n` + `main`)

Format: each instruction line is followed by a short **English** note (`--->`).

```bash
(gdb) disas o
Dump of assembler code for function o:
   0x080484a4 <+0>:     push   %ebp               ---> Prologue.
   0x080484a5 <+1>:     mov    %esp,%ebp          ---> Frame for o().
   0x080484a7 <+3>:     sub    $0x18,%esp         ---> Space for args.
   0x080484aa <+6>:     movl   $0x80485f0,(%esp)  ---> Address of shell command string (e.g. /bin/sh).
   0x080484b1 <+13>:    call   0x80483b0 <system@plt>  ---> system(...) — **target of GOT hijack** (exit→o).
   0x080484b6 <+18>:    movl   $0x1,(%esp)        ---> Status argument for _exit.
   0x080484bd <+25>:    call   0x8048390 <_exit@plt>  ---> _exit(1) — never returns after shell.
End of assembler dump.
(gdb) disas n
Dump of assembler code for function n:
   0x080484c2 <+0>:     push   %ebp               ---> Prologue.
   0x080484c3 <+1>:     mov    %esp,%ebp          ---> Frame for n().
   0x080484c5 <+3>:     sub    $0x218,%esp        ---> Buffer 0x200 bytes + locals.
   0x080484cb <+9>:     mov    0x8049848,%eax     ---> stdin.
   0x080484d0 <+14>:    mov    %eax,0x8(%esp)     ---> fgets stream.
   0x080484d4 <+18>:    movl   $0x200,0x4(%esp)   ---> fgets size 512.
   0x080484dc <+26>:    lea    -0x208(%ebp),%eax   ---> Buffer address.
   0x080484e2 <+32>:    mov    %eax,(%esp)        ---> fgets buffer.
   0x080484e5 <+35>:    call   0x80483a0 <fgets@plt>  ---> fgets(buf, 0x200, stdin).
   0x080484ea <+40>:    lea    -0x208(%ebp),%eax   ---> Buffer address for printf.
   0x080484f0 <+46>:    mov    %eax,(%esp)        ---> Argument to printf.
   0x080484f3 <+49>:    call   0x8048380 <printf@plt>  ---> printf(buf) — **format string** (read flag / write GOT).
   0x080484f8 <+54>:    movl   $0x1,(%esp)        ---> exit(1) argument.
   0x080484ff <+61>:    call   0x80483d0 <exit@plt>  ---> exit(1) — **GOT hijack** redirects here to o().
End of assembler dump.
(gdb) disas main
Dump of assembler code for function main:
   0x08048504 <+0>:     push   %ebp               ---> Prologue.
   0x08048505 <+1>:     mov    %esp,%ebp          ---> Frame setup.
   0x08048507 <+3>:     and    $0xfffffff0,%esp   ---> Align stack.
   0x0804850a <+6>:     call   0x80484c2 <n>      ---> main calls n() only.
   0x0804850f <+11>:    leave                     ---> Epilogue.
   0x08048510 <+12>:    ret                       ---> Return to libc.
End of assembler dump.
(gdb) 
```
