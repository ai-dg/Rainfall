# Level2 — GDB disassembly (`p` + `main`)

Format: each instruction line is followed by a short **English** note (`--->`).

```bash
(gdb) disas p
Dump of assembler code for function p:
   0x080484d4 <+0>:     push   %ebp               ---> Save caller’s frame pointer (prologue).
   0x080484d5 <+1>:     mov    %esp,%ebp          ---> Establish stack frame for p().
   0x080484d7 <+3>:     sub    $0x68,%esp         ---> Allocate stack space (locals + alignment).
   0x080484da <+6>:     mov    0x8049860,%eax     ---> Load stdout pointer (from GOT) into %eax.
   0x080484df <+11>:    mov    %eax,(%esp)        ---> fflush(stdout): only argument = FILE*.
   0x080484e2 <+14>:    call   0x80483b0 <fflush@plt>  ---> Flush stdout before reading input.
   0x080484e7 <+19>:    lea    -0x4c(%ebp),%eax    ---> %eax = address of buf (ebp-0x4c, 76 bytes).
   0x080484ea <+22>:    mov    %eax,(%esp)        ---> Pass buf pointer as argument to gets().
   0x080484ed <+25>:    call   0x80483c0 <gets@plt>  ---> gets(buf): unbounded read → stack overflow.
   0x080484f2 <+30>:    mov    0x4(%ebp),%eax     ---> Load saved return address (word above saved EBP).
   0x080484f5 <+33>:    mov    %eax,-0xc(%ebp)    ---> Store it in local temp (for the check below).
   0x080484f8 <+36>:    mov    -0xc(%ebp),%eax    ---> Reload that value into %eax.
   0x080484fb <+39>:    and    $0xb0000000,%eax   ---> Mask high bits: detect “looks like stack” (0xb…).
   0x08048500 <+44>:    cmp    $0xb0000000,%eax   ---> Compare to 0xb0000000 (stack range heuristic).
   0x08048505 <+49>:    jne    0x8048527 <p+83>   ---> If return address is NOT in that range, skip abort.
   0x08048507 <+51>:    mov    $0x8048620,%eax    ---> Format string address for printf (error path).
   0x0804850c <+56>:    mov    -0xc(%ebp),%edx    ---> The return address value as second arg.
   0x0804850f <+59>:    mov    %edx,0x4(%esp)     ---> Set up printf arguments on stack.
   0x08048513 <+63>:    mov    %eax,(%esp)        ---> First arg: format string.
   0x08048516 <+66>:    call   0x80483a0 <printf@plt>  ---> Print blocked return (then _exit).
   0x0804851b <+71>:    movl   $0x1,(%esp)        ---> Argument to _exit (status 1).
   0x08048522 <+78>:    call   0x80483d0 <_exit@plt>  ---> Abort: cannot return directly to stack.
   0x08048527 <+83>:    lea    -0x4c(%ebp),%eax    ---> Normal path: %eax = &buf again.
   0x0804852a <+86>:    mov    %eax,(%esp)        ---> Argument for puts().
   0x0804852d <+89>:    call   0x80483f0 <puts@plt>  ---> puts(buf) — echoes user input.
   0x08048532 <+94>:    lea    -0x4c(%ebp),%eax    ---> %eax = &buf again.
   0x08048535 <+97>:    mov    %eax,(%esp)        ---> Argument for strdup().
   0x08048538 <+100>:   call   0x80483e0 <strdup@plt>  ---> strdup(buf) — heap copy of buffer.
   0x0804853d <+105>:   leave                     ---> Epilogue: restore %ebp/%esp.
   0x0804853e <+106>:   ret                       ---> Return to main (or overwritten address if exploited).
End of assembler dump.
(gdb) disas main
Dump of assembler code for function main:
   0x0804853f <+0>:     push   %ebp               ---> Prologue.
   0x08048540 <+1>:     mov    %esp,%ebp          ---> Frame setup.
   0x08048542 <+3>:     and    $0xfffffff0,%esp   ---> Align stack to 16 bytes.
   0x08048545 <+6>:     call   0x80484d4 <p>      ---> main() only calls p() — all logic in p.
   0x0804854a <+11>:    leave                     ---> Epilogue.
   0x0804854b <+12>:    ret                       ---> Return to libc start / exit.
End of assembler dump.
(gdb) 
```
