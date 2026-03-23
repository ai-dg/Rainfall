# Level3 — GDB disassembly (`v` + `main`)

Format: each instruction line is followed by a short **English** note (`--->`).

```bash
(gdb) disas v
Dump of assembler code for function v:
   0x080484a4 <+0>:     push   %ebp               ---> Prologue: save frame pointer.
   0x080484a5 <+1>:     mov    %esp,%ebp          ---> New stack frame for v().
   0x080484a7 <+3>:     sub    $0x218,%esp        ---> Large stack frame (buffer ~0x200 + locals).
   0x080484ad <+9>:     mov    0x8049860,%eax     ---> Load stdin (FILE*) from GOT.
   0x080484b2 <+14>:    mov    %eax,0x8(%esp)     ---> 3rd arg to fgets: stream = stdin.
   0x080484b6 <+18>:    movl   $0x200,0x4(%esp)   ---> 2nd arg: max size 0x200 (512) bytes.
   0x080484be <+26>:    lea    -0x208(%ebp),%eax   ---> %eax = address of local buffer (ebp-0x208).
   0x080484c4 <+32>:    mov    %eax,(%esp)        ---> 1st arg: buffer pointer.
   0x080484c7 <+35>:    call   0x80483a0 <fgets@plt>  ---> fgets(buf, 0x200, stdin) — bounded read.
   0x080484cc <+40>:    lea    -0x208(%ebp),%eax   ---> %eax = same buffer address.
   0x080484d2 <+46>:    mov    %eax,(%esp)        ---> Argument to printf (format string / user data).
   0x080484d5 <+49>:    call   0x8048390 <printf@plt>  ---> printf(buf) — **format string vulnerability** if buf contains %.
   0x080484da <+54>:    mov    0x804988c,%eax      ---> Load global variable m into %eax.
   0x080484df <+59>:    cmp    $0x40,%eax         ---> Compare m to 0x40 (64).
   0x080484e2 <+62>:    jne    0x8048518 <v+116>   ---> If m != 64, skip win branch.
   0x080484e4 <+64>:    mov    0x8049880,%eax     ---> Load stdout for fwrite.
   0x080484e9 <+69>:    mov    %eax,%edx          ---> Copy FILE* to %edx.
   0x080484eb <+71>:    mov    $0x8048600,%eax    ---> Pointer to string constant for fwrite.
   0x080484f0 <+76>:    mov    %edx,0xc(%esp)     ---> 4th arg: stream (stdout).
   0x080484f4 <+80>:    movl   $0xc,0x8(%esp)     ---> 3rd arg: count 12 bytes.
   0x080484fc <+88>:    movl   $0x1,0x4(%esp)     ---> 2nd arg: size 1.
   0x08048504 <+96>:    mov    %eax,(%esp)        ---> 1st arg: message buffer.
   0x08048507 <+99>:    call   0x80483b0 <fwrite@plt>  ---> Print “You win!”-style message.
   0x0804850c <+104>:   movl   $0x804860d,(%esp)        ---> Load address of "/bin/sh" (or similar).
   0x08048513 <+111>:   call   0x80483c0 <system@plt>  ---> system("/bin/sh") — shell when m == 64.
   0x08048518 <+116>:   leave                     ---> Epilogue.
   0x08048519 <+117>:   ret                       ---> Return to main.
End of assembler dump.
(gdb) disas main
Dump of assembler code for function main:
   0x0804851a <+0>:     push   %ebp               ---> Prologue.
   0x0804851b <+1>:     mov    %esp,%ebp          ---> Frame setup.
   0x0804851d <+3>:     and    $0xfffffff0,%esp   ---> Align stack.
   0x08048520 <+6>:     call   0x80484a4 <v>      ---> main() calls v() only.
   0x08048525 <+11>:    leave                     ---> Epilogue.
   0x08048526 <+12>:    ret                       ---> Return to libc.
End of assembler dump.
```

**GDB:** `info variables` — global **`m`** is typically at **`0x0804988c`** (written with **`%n`** from the format string; target value **`0x40`** for the win branch).

