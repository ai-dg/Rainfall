# Level8 — Analyse technique

## Binaire

- ELF 32-bit i386, setuid setgid level9.
- Imports : printf, free, strdup, fgets, fwrite, strcpy, malloc, **system**.
- Commandes : **auth** , **reset**, **service**, **login**. Chaîne "/bin/sh" en .rodata.

## Variables globales

- **auth** (0x8049aac) : pointeur vers un bloc malloc(4).
- **service** (0x8049ab0) : pointeur vers une chaîne (strdup).

## Flux main (boucle)

1. **printf("%p, %p ", auth, service)** puis **fgets(buffer, 0x80, stdin)**.
2. Si entrée = **"auth "** (5 caractères) : malloc(4) → auth, *auth=0, **strcpy(auth, input+5)** si strlen(input+5) ≤ 0x1e (30). → **Overflow** : on copie jusqu’à 30 octets dans un bloc de 4.
3. Si entrée = **"reset"** : free(auth).
4. Si entrée = **"service"** (6 caractères) : **strdup(input+7)** → service.
5. Si entrée = **"login"** : si ***(auth+0x20) != 0** → **system("/bin/sh")**, sinon fwrite("Password:\n", ...).

## Vulnérabilité

- **auth** ne fait que 4 octets ; le strcpy peut en écrire jusqu’à 30 → overflow, mais on n’atteint pas auth+0x20 (32) avec seulement "auth " + 30 octets (on va jusqu’à auth+29).
- ***(auth+0x20)** est donc lu **dans le heap** après le bloc auth. Si une allocation **service** (strdup) est placée juste après auth, auth+0x20 peut tomber **dans le buffer service**. En envoyant **"service" + une longue chaîne**, les octets écrits par strdup remplissent ce buffer ; un octet non nul à l’offset correspondant suffit pour que login appelle system("/bin/sh").

## Exploit

1. **auth** suivi d’un court argument (ex. **auth AAAA**) pour allouer auth et éviter reset.
2. **service** suivi d’une chaîne d’au moins **21 octets** (ex. **service** + 21×'A') pour que l’allocation strdup soit après auth et que auth+0x20 tombe dans ce buffer (avec en-têtes de chunk, auth+0x20 ≈ service+20).
3. **login** → *(auth+0x20) non nul → system("/bin/sh").

Sur certaines VM il faut plus de 21 octets (ex. 32) selon le layout du heap.

## Adresses utiles

| Élément   | Valeur     |
|----------|------------|
| auth     | 0x8049aac  |
| service  | 0x8049ab0  |
| /bin/sh  | 0x8048833  |
