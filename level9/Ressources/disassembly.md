# Level9 — GDB disassembly (`main` + `N::N` + `setAnnotation` + `operator new`)

Format: each instruction line is followed by a short **English** note (`--->`).

```bash
(gdb) disas main
Dump of assembler code for function main:
   0x080485f4 <+0>:     push   %ebp               ---> Prologue.
   0x080485f5 <+1>:     mov    %esp,%ebp          ---> Frame for main().
   0x080485f7 <+3>:     push   %ebx               ---> Save ebx (holds object pointers).
   0x080485f8 <+4>:     and    $0xfffffff0,%esp   ---> Align stack.
   0x080485fb <+7>:     sub    $0x20,%esp         ---> Local slots for two N* and temps.
   0x080485fe <+10>:    cmpl   $0x1,0x8(%ebp)     ---> Compare argc to 1 (need argv[1]).
   0x08048602 <+14>:    jg     0x8048610 <main+28>  ---> If argc > 1, continue.
   0x08048604 <+16>:    movl   $0x1,(%esp)        ---> _exit(1) status.
   0x0804860b <+23>:    call   0x80484f0 <_exit@plt>  ---> **argc <= 1** → abort (need argument).
   0x08048610 <+28>:    movl   $0x6c,(%esp)       ---> **operator new(0x6c)** — sizeof(N) = 108 bytes.
   0x08048617 <+35>:    call   0x8048530 <_Znwj@plt>  ---> Allocate first object **a**.
   0x0804861c <+40>:    mov    %eax,%ebx          ---> %ebx = raw pointer to first N.
   0x0804861e <+42>:    movl   $0x5,0x4(%esp)     ---> Constructor 2nd arg: int value **5**.
   0x08048626 <+50>:    mov    %ebx,(%esp)        ---> **this** pointer for N::N(int).
   0x08048629 <+53>:    call   0x80486f6 <_ZN1NC2Ei>  ---> **N::N(this, 5)** — init vtable + field.
   0x0804862e <+58>:    mov    %ebx,0x1c(%esp)    ---> Save **a** on stack.
   0x08048632 <+62>:    movl   $0x6c,(%esp)       ---> operator new(0x6c) for second object.
   0x08048639 <+69>:    call   0x8048530 <_Znwj@plt>  ---> Allocate **b**.
   0x0804863e <+74>:    mov    %eax,%ebx          ---> %ebx = pointer to second N.
   0x08048640 <+76>:    movl   $0x6,0x4(%esp)     ---> Constructor arg: value **6**.
   0x08048648 <+84>:    mov    %ebx,(%esp)        ---> **this** for second N::N.
   0x0804864b <+87>:    call   0x80486f6 <_ZN1NC2Ei>  ---> **N::N(this, 6)**.
   0x08048650 <+92>:    mov    %ebx,0x18(%esp)    ---> Save **b**.
   0x08048654 <+96>:    mov    0x1c(%esp),%eax    ---> Load **a**.
   0x08048658 <+100>:   mov    %eax,0x14(%esp)    ---> First arg to setAnnotation: **this = a**.
   0x0804865c <+104>:   mov    0x18(%esp),%eax    ---> Load **b** (unused here, setup).
   0x08048660 <+108>:   mov    %eax,0x10(%esp)    ---> Keep **b** handy.
   0x08048664 <+112>:   mov    0xc(%ebp),%eax     ---> argv.
   0x08048667 <+115>:   add    $0x4,%eax          ---> &argv[1].
   0x0804866a <+118>:   mov    (%eax),%eax        ---> argv[1] — user payload.
   0x0804866c <+120>:   mov    %eax,0x4(%esp)     ---> **setAnnotation(this, argv[1])** — 2nd arg.
   0x08048670 <+124>:   mov    0x14(%esp),%eax    ---> **this = a**.
   0x08048674 <+128>:   mov    %eax,(%esp)        ---> 1st arg: pointer to first object.
   0x08048677 <+131>:   call   0x804870e <_ZN1N13setAnnotationEPc>  ---> **memcpy** into a->annotation — **heap overflow** into **b** (vtable).
   0x0804867c <+136>:   mov    0x10(%esp),%eax    ---> Load **b**.
   0x08048680 <+140>:   mov    (%eax),%eax        ---> Load **b->vtable** (first word of object).
   0x08048682 <+142>:   mov    (%eax),%edx        ---> Load **vtable[0]** — function pointer for virtual call.
   0x08048684 <+144>:   mov    0x14(%esp),%eax    ---> **a** again.
   0x08048688 <+148>:   mov    %eax,0x4(%esp)     ---> 2nd arg to virtual call: **a** (N*).
   0x0804868c <+152>:   mov    0x10(%esp),%eax    ---> **b** (this for call).
   0x08048690 <+156>:   mov    %eax,(%esp)        ---> 1st arg: **this = b**.
   0x08048693 <+159>:   call   *%edx              ---> **Indirect call** — vtable dispatch; hijacked → shellcode / win.
   0x08048695 <+161>:   mov    -0x4(%ebp),%ebx    ---> Restore saved ebx.
   0x08048698 <+164>:   leave                     ---> Epilogue.
   0x08048699 <+165>:   ret                       ---> Return to libc.
End of assembler dump.
(gdb) disas _Znwj
Dump of assembler code for function _Znwj@plt:
   0x08048530 <+0>:     jmp    *0x8049b70         ---> PLT trampoline: jump to resolved **operator new** in libc.
   0x08048536 <+6>:     push   $0x40              ---> Lazy binding index / push reloc slot.
   0x0804853b <+11>:    jmp    0x80484a0          ---> Resolve GOT then jump to real symbol.
End of assembler dump.
(gdb) disas _ZN1NC2Ei
Dump of assembler code for function _ZN1NC2Ei:
   0x080486f6 <+0>:     push   %ebp               ---> Prologue.
   0x080486f7 <+1>:     mov    %esp,%ebp          ---> Frame for constructor.
   0x080486f9 <+3>:     mov    0x8(%ebp),%eax     ---> **this** pointer (N*).
   0x080486fc <+6>:     movl   $0x8048848,(%eax)   ---> Write **vtable pointer** at object start (+0).
   0x08048702 <+12>:    mov    0x8(%ebp),%eax     ---> Reload **this**.
   0x08048705 <+15>:    mov    0xc(%ebp),%edx     ---> Constructor int parameter **v** (5 or 6).
   0x08048708 <+18>:    mov    %edx,0x68(%eax)    ---> Store int at **this+0x68** (after annotation region).
   0x0804870b <+21>:    pop    %ebp               ---> Epilogue (small frame).
   0x0804870c <+22>:    ret                       ---> Return to main.
End of assembler dump.
(gdb) disas _ZN1N13setAnnotationEPc
Dump of assembler code for function _ZN1N13setAnnotationEPc:
   0x0804870e <+0>:     push   %ebp               ---> Prologue.
   0x0804870f <+1>:     mov    %esp,%ebp          ---> Frame.
   0x08048711 <+3>:     sub    $0x18,%esp         ---> Arg area for strlen/memcpy.
   0x08048714 <+6>:     mov    0xc(%ebp),%eax     ---> **char* s** (argv[1]).
   0x08048717 <+9>:     mov    %eax,(%esp)        ---> strlen(s).
   0x0804871a <+12>:    call   0x8048520 <strlen@plt>  ---> Compute length of user string.
   0x0804871f <+17>:    mov    0x8(%ebp),%edx     ---> **this**.
   0x08048722 <+20>:    add    $0x4,%edx          ---> **this+4** — start of **annotation[]** (after vptr).
   0x08048725 <+23>:    mov    %eax,0x8(%esp)     ---> memcpy **n** = strlen (no cap → overflow).
   0x08048729 <+27>:    mov    0xc(%ebp),%eax     ---> **src** = s.
   0x0804872c <+30>:    mov    %eax,0x4(%esp)     ---> memcpy second arg.
   0x08048730 <+34>:    mov    %edx,(%esp)        ---> memcpy **dst** = this+4.
   0x08048733 <+37>:    call   0x8048510 <memcpy@plt>  ---> **memcpy(annotation, argv[1], strlen)** — overwrites next chunk / **b**’s vptr.
   0x08048738 <+42>:    leave                     ---> Epilogue.
   0x08048739 <+43>:    ret                       ---> Return to main.
End of assembler dump.
(gdb) 
```

**Note:** vtable for **N** and **typeinfo** live in `.rodata`; the exploit overwrites **`b`’s vptr** then uses the virtual call.

