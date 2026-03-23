# Level1 — GDB disassembly (`main` + `run`)

Format: each instruction line is followed by a short **English** note (`--->`).

```bash
Dump of assembler code for function main:
   0x08048480 <+0>:     push   %ebp               ---> Save the caller’s frame pointer on the stack (function prologue).
   0x08048481 <+1>:     mov    %esp,%ebp          ---> Make %ebp the frame base for this stack frame.
   0x08048483 <+3>:     and    $0xfffffff0,%esp   ---> Align %esp down to a 16-byte boundary (ABI / compiler convention).
   0x08048486 <+6>:     sub    $0x50,%esp         ---> Reserve 0x50 (80) bytes on the stack for locals and outgoing args.
   0x08048489 <+9>:     lea    0x10(%esp),%eax     ---> Compute address of local buffer: %eax = buf (here %esp+0x10).
   0x0804848d <+13>:    mov    %eax,(%esp)        ---> Pass that pointer as the argument to gets (first/only arg on stack).
   0x08048490 <+16>:    call   0x8048340 <gets@plt>  ---> Call gets(buf): unbounded read → stack overflow if input is too long.
   0x08048495 <+21>:    leave                     ---> Tear down the frame: restore %esp and %ebp (function epilogue).
   0x08048496 <+22>:    ret                       ---> Return to the caller using the saved return address on the stack.
End of assembler dump.
(gdb) disas run
Dump of assembler code for function run:
   0x08048444 <+0>:     push   %ebp               ---> Save the caller’s frame pointer (prologue).
   0x08048445 <+1>:     mov    %esp,%ebp          ---> Set up the stack frame for run().
   0x08048447 <+3>:     sub    $0x18,%esp         ---> Allocate 0x18 (24) bytes for saved regs / outgoing call arguments.
   0x0804844a <+6>:     mov    0x80497c0,%eax     ---> Load a pointer (here stdout) from the GOT/data into %eax.
   0x0804844f <+11>:    mov    %eax,%edx          ---> Copy it to %edx (will be the FILE* for fwrite).
   0x08048451 <+13>:    mov    $0x8048570,%eax    ---> Load address of the format string ("Good... Wait what?\n") into %eax.
   0x08048456 <+18>:    mov    %edx,0xc(%esp)     ---> 4th arg to fwrite: stream (stdout).
   0x0804845a <+22>:    movl   $0x13,0x8(%esp)    ---> 3rd arg: count = 0x13 (19) bytes.
   0x08048462 <+30>:    movl   $0x1,0x4(%esp)     ---> 2nd arg: size = 1 byte per element.
   0x0804846a <+38>:    mov    %eax,(%esp)        ---> 1st arg: pointer to the string buffer.
   0x0804846d <+41>:    call   0x8048350 <fwrite@plt>  ---> fwrite("Good... Wait what?\n", 1, 19, stdout).
   0x08048472 <+46>:    movl   $0x8048584,(%esp)  ---> Put address of "/bin/sh" string as argument for system().
   0x08048479 <+53>:    call   0x8048360 <system@plt>  ---> system("/bin/sh") → spawns a shell (goal of redirecting EIP to run).
   0x0804847e <+58>:    leave                     ---> Restore frame pointer and stack pointer (epilogue).
   0x0804847f <+59>:    ret                       ---> Return to whoever called run() (normally not reached from main in normal flow).
End of assembler dump.
(gdb) 
```
