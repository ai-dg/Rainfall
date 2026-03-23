# Level6 — GDB disassembly (`n` + `m` + `main`)

Format: each instruction line is followed by a short **English** note (`--->`).

```bash
(gdb) disas n
Dump of assembler code for function n:
   0x08048454 <+0>:     push   %ebp               ---> Prologue.
   0x08048455 <+1>:     mov    %esp,%ebp          ---> Frame for n() — **win function** (shell).
   0x08048457 <+3>:     sub    $0x18,%esp         ---> Allocate arg area.
   0x0804845a <+6>:     movl   $0x80485b0,(%esp)  ---> Address of shell command string.
   0x08048461 <+13>:    call   0x8048370 <system@plt>  ---> system("/bin/sh") or similar.
   0x08048466 <+18>:    leave                     ---> Epilogue.
   0x08048467 <+19>:    ret                       ---> Return to caller (not used if EIP→n).
End of assembler dump.
(gdb) disas m
Dump of assembler code for function m:
   0x08048468 <+0>:     push   %ebp               ---> Prologue.
   0x08048469 <+1>:     mov    %esp,%ebp          ---> Frame for m().
   0x0804846b <+3>:     sub    $0x18,%esp         ---> Allocate arg area.
   0x0804846e <+6>:     movl   $0x80485d1,(%esp)  ---> Address of “unsafe” message string.
   0x08048475 <+13>:    call   0x8048360 <puts@plt>  ---> puts(...) — normal path after strcpy.
   0x0804847a <+18>:    leave                     ---> Epilogue.
   0x0804847b <+19>:    ret                       ---> Return to main.
End of assembler dump.
(gdb) disas main
Dump of assembler code for function main:
   0x0804847c <+0>:     push   %ebp               ---> Prologue.
   0x0804847d <+1>:     mov    %esp,%ebp          ---> Frame for main().
   0x0804847f <+3>:     and    $0xfffffff0,%esp   ---> Align stack to 16 bytes.
   0x08048482 <+6>:     sub    $0x20,%esp         ---> Locals: two pointers + padding.
   0x08048485 <+9>:     movl   $0x40,(%esp)       ---> malloc(0x40) — 64 bytes for first chunk.
   0x0804848c <+16>:    call   0x8048350 <malloc@plt>  ---> Allocate buffer 1.
   0x08048491 <+21>:    mov    %eax,0x1c(%esp)    ---> Store pointer at esp+0x1c (first chunk).
   0x08048495 <+25>:    movl   $0x4,(%esp)        ---> malloc(4) — small second chunk.
   0x0804849c <+32>:    call   0x8048350 <malloc@plt>  ---> Allocate buffer 2.
   0x080484a1 <+37>:    mov    %eax,0x18(%esp)    ---> Store second pointer at esp+0x18.
   0x080484a5 <+41>:    mov    $0x8048468,%edx    ---> Address of **n** (win function) stored in the small chunk’s first word.
   0x080484aa <+46>:    mov    0x18(%esp),%eax    ---> Pointer to small chunk.
   0x080484ae <+50>:    mov    %edx,(%eax)        ---> Write **address of n** into small chunk (first word).
   0x080484b0 <+52>:    mov    0xc(%ebp),%eax     ---> Load argv (char **argv).
   0x080484b3 <+55>:    add    $0x4,%eax          ---> %eax = &argv[1] (skip argv[0]).
   0x080484b6 <+58>:    mov    (%eax),%eax        ---> %eax = argv[1] (user string).
   0x080484b8 <+60>:    mov    %eax,%edx          ---> Copy source pointer for strcpy.
   0x080484ba <+62>:    mov    0x1c(%esp),%eax    ---> Pointer to large 0x40 buffer.
   0x080484be <+66>:    mov    %edx,0x4(%esp)     ---> strcpy(src, argv[1]) — src second arg.
   0x080484c2 <+70>:    mov    %eax,(%esp)        ---> strcpy dest = large buffer.
   0x080484c5 <+73>:    call   0x8048340 <strcpy@plt>  ---> **Heap overflow** if argv[1] > 64 bytes.
   0x080484ca <+78>:    mov    0x18(%esp),%eax    ---> Load pointer to small chunk.
   0x080484ce <+82>:    mov    (%eax),%eax        ---> Dereference: load function pointer (now n).
   0x080484d0 <+84>:    call   *%eax              ---> **Indirect call** — jumps to n() if overwritten.
   0x080484d2 <+86>:    leave                     ---> Epilogue.
   0x080484d3 <+87>:    ret                       ---> Return to libc.
End of assembler dump.
(gdb) 
```
