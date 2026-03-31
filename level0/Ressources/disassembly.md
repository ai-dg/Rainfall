# Level0 — GDB disassembly (`main`)

Format: each instruction line is followed by a short **English** note (`--->`).

```bash
(gdb) disas main
Dump of assembler code for function main:
   0x08048ec0 <+0>:     push   %ebp               ---> Prologue: save caller’s frame pointer.
   0x08048ec1 <+1>:     mov    %esp,%ebp          ---> Establish stack frame for main().
   0x08048ec3 <+3>:     and    $0xfffffff0,%esp   ---> Align %esp to 16 bytes (ABI).
   0x08048ec6 <+6>:     sub    $0x20,%esp         ---> Reserve 0x20 bytes for locals / outgoing args.
   0x08048ec9 <+9>:     mov    0xc(%ebp),%eax     ---> Load argv (char **argv) from the stack frame.
   0x08048ecc <+12>:    add    $0x4,%eax          ---> %eax = &argv[1] (skip argv[0]).
   0x08048ecf <+15>:    mov    (%eax),%eax        ---> %eax = argv[1] (pointer to user string).
   0x08048ed1 <+17>:    mov    %eax,(%esp)        ---> Pass argv[1] as the argument to atoi().
   0x08048ed4 <+20>:    call   0x8049710 <atoi>   ---> atoi(argv[1]) → result in %eax.
   0x08048ed9 <+25>:    cmp    $0x1a7,%eax        ---> **Backdoor:** compare to magic **0x1a7** (423 decimal).
   0x08048ede <+30>:    jne    0x8048f58 <main+152>  ---> If not equal → fail path ("No !\n").
   0x08048ee0 <+32>:    movl   $0x80c5348,(%esp)  ---> Address of `"/bin/sh"` in .rodata for strdup().
   0x08048ee7 <+39>:    call   0x8050bf0 <strdup> ---> Duplicate string → pointer to heap copy.
   0x08048eec <+44>:    mov    %eax,0x10(%esp)    ---> Store strdup result (shell path) on stack.
   0x08048ef0 <+48>:    movl   $0x0,0x14(%esp)    ---> argv[1] = NULL — end of execv argv array {sh, NULL}.
   0x08048ef8 <+56>:    call   0x8054680 <getegid> ---> Read effective group id (setuid context).
   0x08048efd <+61>:    mov    %eax,0x1c(%esp)    ---> Save egid in a local slot.
   0x08048f01 <+65>:    call   0x8054670 <geteuid> ---> Read effective user id.
   0x08048f06 <+70>:    mov    %eax,0x18(%esp)    ---> Save euid.
   0x08048f0a <+74>:    mov    0x1c(%esp),%eax    ---> Load egid for setresgid triple.
   0x08048f0e <+78>:    mov    %eax,0x8(%esp)     ---> 3rd arg: rgid.
   0x08048f12 <+82>:    mov    0x1c(%esp),%eax    ---> Reload egid.
   0x08048f16 <+86>:    mov    %eax,0x4(%esp)     ---> 2nd arg: egid.
   0x08048f1a <+90>:    mov    0x1c(%esp),%eax    ---> Reload egid.
   0x08048f1e <+94>:    mov    %eax,(%esp)        ---> 1st arg: real gid.
   0x08048f21 <+97>:    call   0x8054700 <setresgid>  ---> setresgid(egid, egid, egid) — drop extra groups.
   0x08048f26 <+102>:   mov    0x18(%esp),%eax    ---> Load euid for setresuid.
   0x08048f2a <+106>:   mov    %eax,0x8(%esp)     ---> 3rd arg: ruid.
   0x08048f2e <+110>:   mov    0x18(%esp),%eax    ---> Reload euid.
   0x08048f32 <+114>:   mov    %eax,0x4(%esp)     ---> 2nd arg: euid.
   0x08048f36 <+118>:   mov    0x18(%esp),%eax    ---> Reload euid.
   0x08048f3a <+122>:   mov    %eax,(%esp)        ---> 1st arg: real uid.
   0x08048f3d <+125>:   call   0x8054690 <setresuid>  ---> setresuid(euid, euid, euid) — align real IDs to effective.
   0x08048f42 <+130>:   lea    0x10(%esp),%eax    ---> %eax = &argv[0] for execv (pointer to {sh, NULL}).
   0x08048f46 <+134>:   mov    %eax,0x4(%esp)     ---> 2nd arg to execv: char **argv.
   0x08048f4a <+138>:   movl   $0x80c5348,(%esp)  ---> 1st arg: pathname `"/bin/sh"` (same rodata string).
   0x08048f51 <+145>:   call   0x8054640 <execv>  ---> execv("/bin/sh", { strdup’d path, NULL }) — shell with euid.
   0x08048f56 <+150>:   jmp    0x8048f80 <main+192>  ---> Skip fail path; fall through to exit(0) epilogue.
   0x08048f58 <+152>:   mov    0x80ee170,%eax     ---> Load **stderr** (FILE*) from data (e.g. GOT).
   0x08048f5d <+157>:   mov    %eax,%edx          ---> FILE* for fwrite.
   0x08048f5f <+159>:   mov    $0x80c5350,%eax    ---> Address of `"No !\n"` in .rodata.
   0x08048f64 <+164>:   mov    %edx,0xc(%esp)     ---> 4th arg: stream (stderr).
   0x08048f68 <+168>:   movl   $0x5,0x8(%esp)     ---> 3rd arg: count = 5 bytes.
   0x08048f70 <+176>:   movl   $0x1,0x4(%esp)     ---> 2nd arg: size = 1.
   0x08048f78 <+184>:   mov    %eax,(%esp)        ---> 1st arg: buffer = "No !\n".
   0x08048f7b <+187>:   call   0x804a230 <fwrite> ---> fwrite("No !\n", 1, 5, stderr) — wrong magic.
   0x08048f80 <+192>:   mov    $0x0,%eax          ---> Return 0 from main (success path after execv not reached if shell replaces process).
   0x08048f85 <+197>:   leave                     ---> Epilogue: restore %ebp and %esp.
   0x08048f86 <+198>:   ret                       ---> Return to libc (or process image replaced by execv).
End of assembler dump.
(gdb)
```

**Magic check:** `cmp $0x1a7,%eax` at **`<main+25>`** — pass with **`./level0 423`** (`atoi` → **0x1a7**).  
**Strings (this build):** `"/bin/sh"` at **0x080c5348**, `"No !\n"` at **0x080c5350** — addresses may differ if you recompile; use `x/s` / `objdump -s` on your binary.
