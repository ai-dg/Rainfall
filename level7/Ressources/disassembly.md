# Level7 — GDB disassembly (`m` + `main`)

Format: each instruction line is followed by a short **English** note (`--->`).

```bash
(gdb) disas m
Dump of assembler code for function m:
   0x080484f4 <+0>:     push   %ebp               ---> Prologue.
   0x080484f5 <+1>:     mov    %esp,%ebp          ---> Frame for m().
   0x080484f7 <+3>:     sub    $0x18,%esp         ---> Arg area for printf.
   0x080484fa <+6>:     movl   $0x0,(%esp)        ---> time(NULL): arg = NULL.
   0x08048501 <+13>:    call   0x80483d0 <time@plt>  ---> time(&t) simplified as time(0).
   0x08048506 <+18>:    mov    $0x80486e0,%edx    ---> Format string "%s - %d\n" (or similar).
   0x0804850b <+23>:    mov    %eax,0x8(%esp)     ---> 3rd arg to printf: time value.
   0x0804850f <+27>:    movl   $0x8049960,0x4(%esp)  ---> 2nd arg: address of global buffer **c** (pass content).
   0x08048517 <+35>:    mov    %edx,(%esp)        ---> 1st arg: format string.
   0x0804851a <+38>:    call   0x80483b0 <printf@plt>  ---> printf(fmt, c, time) — **GOT hijack on puts** prints c with .pass.
   0x0804851f <+43>:    leave                     ---> Epilogue.
   0x08048520 <+44>:    ret                       ---> Return.
End of assembler dump.
(gdb) disas main
Dump of assembler code for function main:
   0x08048521 <+0>:     push   %ebp               ---> Prologue.
   0x08048522 <+1>:     mov    %esp,%ebp          ---> Frame for main().
   0x08048524 <+3>:     and    $0xfffffff0,%esp   ---> Align stack.
   0x08048527 <+6>:     sub    $0x20,%esp         ---> Local slots for heap pointers.
   0x0804852a <+9>:     movl   $0x8,(%esp)        ---> malloc(8) — first small chunk.
   0x08048531 <+16>:    call   0x80483f0 <malloc@plt>  ---> Allocate ptr1 chunk.
   0x08048536 <+21>:    mov    %eax,0x1c(%esp)    ---> Save ptr1.
   0x0804853a <+25>:    mov    0x1c(%esp),%eax    ---> Load ptr1.
   0x0804853e <+29>:    movl   $0x1,(%eax)        ---> *(int*)ptr1 = 1 (tag field).
   0x08048544 <+35>:    movl   $0x8,(%esp)        ---> malloc(8) — buf1.
   0x0804854b <+42>:    call   0x80483f0 <malloc@plt>  ---> Allocate data buffer for first pair.
   0x08048550 <+47>:    mov    %eax,%edx          ---> buf1 pointer in %edx.
   0x08048552 <+49>:    mov    0x1c(%esp),%eax    ---> ptr1 again.
   0x08048556 <+53>:    mov    %edx,0x4(%eax)     ---> ptr1->next = buf1 (word at offset +4).
   0x08048559 <+56>:    movl   $0x8,(%esp)        ---> malloc(8) — second small chunk (ptr2).
   0x08048560 <+63>:    call   0x80483f0 <malloc@plt>  ---> Allocate ptr2.
   0x08048565 <+68>:    mov    %eax,0x18(%esp)    ---> Save ptr2.
   0x08048569 <+72>:    mov    0x18(%esp),%eax    ---> Load ptr2.
   0x0804856d <+76>:    movl   $0x2,(%eax)        ---> *(int*)ptr2 = 2.
   0x08048573 <+82>:    movl   $0x8,(%esp)        ---> malloc(8) — buf2.
   0x0804857a <+89>:    call   0x80483f0 <malloc@plt>  ---> Allocate second data buffer.
   0x0804857f <+94>:    mov    %eax,%edx          ---> buf2 in %edx.
   0x08048581 <+96>:    mov    0x18(%esp),%eax    ---> ptr2.
   0x08048585 <+100>:   mov    %edx,0x4(%eax)     ---> ptr2->next = buf2.
   0x08048588 <+103>:   mov    0xc(%ebp),%eax     ---> argv.
   0x0804858b <+106>:   add    $0x4,%eax          ---> &argv[1].
   0x0804858e <+109>:   mov    (%eax),%eax        ---> argv[1].
   0x08048590 <+111>:   mov    %eax,%edx          ---> Source for first strcpy.
   0x08048592 <+113>:   mov    0x1c(%esp),%eax    ---> ptr1.
   0x08048596 <+117>:   mov    0x4(%eax),%eax     ---> buf1 = ptr1->next.
   0x08048599 <+120>:   mov    %edx,0x4(%esp)     ---> strcpy(src) = argv[1].
   0x0804859d <+124>:   mov    %eax,(%esp)        ---> strcpy(dst) = buf1.
   0x080485a0 <+127>:   call   0x80483e0 <strcpy@plt>  ---> **strcpy(buf1, argv[1])** — overflow corrupts ptr2 / buf2 ptr.
   0x080485a5 <+132>:   mov    0xc(%ebp),%eax     ---> argv.
   0x080485a8 <+135>:   add    $0x8,%eax          ---> &argv[2].
   0x080485ab <+138>:   mov    (%eax),%eax        ---> argv[2].
   0x080485ad <+140>:   mov    %eax,%edx          ---> Source for second strcpy.
   0x080485af <+142>:   mov    0x18(%esp),%eax    ---> ptr2.
   0x080485b3 <+146>:   mov    0x4(%eax),%eax     ---> buf2 = ptr2->next (may be **overwritten**).
   0x080485b6 <+149>:   mov    %edx,0x4(%esp)     ---> strcpy src = argv[2].
   0x080485ba <+153>:   mov    %eax,(%esp)        ---> strcpy dst = *corrupted* pointer.
   0x080485bd <+156>:   call   0x80483e0 <strcpy@plt>  ---> **strcpy(buf2, argv[2])** — arbitrary write (e.g. GOT).
   0x080485c2 <+161>:   mov    $0x80486e9,%edx    ---> Path string part 1 (e.g. "/home/user/level8/.pass").
   0x080485c7 <+166>:   mov    $0x80486eb,%eax    ---> Mode string "r" (or path continuation).
   0x080485cc <+171>:   mov    %edx,0x4(%esp)     ---> fopen second arg.
   0x080485d0 <+175>:   mov    %eax,(%esp)        ---> fopen first arg.
   0x080485d3 <+178>:   call   0x8048430 <fopen@plt>  ---> fopen(".pass", "r") — read secret into global c.
   0x080485d8 <+183>:   mov    %eax,0x8(%esp)     ---> FILE* for fgets.
   0x080485dc <+187>:   movl   $0x44,0x4(%esp)    ---> Read size 0x44 (68) bytes.
   0x080485e4 <+195>:   movl   $0x8049960,(%esp)  ---> Buffer **c** (global).
   0x080485eb <+202>:   call   0x80483c0 <fgets@plt>  ---> fgets(c, 0x44, f).
   0x080485f0 <+207>:   movl   $0x8048703,(%esp)  ---> Address of short string for puts (e.g. "~~").
   0x080485f7 <+214>:   call   0x8048400 <puts@plt>  ---> puts("~~") — **GOT hijack** turns this into m().
   0x080485fc <+219>:   mov    $0x0,%eax          ---> return 0.
   0x08048601 <+224>:   leave                     ---> Epilogue.
   0x08048602 <+225>:   ret                       ---> Return to libc.
End of assembler dump.
# Global **c** at 0x08049960 — holds .pass after fgets; printed via m() after GOT overwrite.
(gdb) 
```
