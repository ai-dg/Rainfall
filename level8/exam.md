# Level8 - Exam Notes

## 1. Objective
Obtenir un shell level9. Commandes : **auth**, **reset**, **service**, **login**. **login** exécute `system("/bin/sh")` si l’octet à **(auth+0x20)** est non nul.

## 2. Copy the binary (extraction)
Depuis l’hôte :
```bash
sshpass -p '<level8_password>' scp -o StrictHostKeyChecking=no -P 4242 level8@localhost:level8 ./level8.bin
```
Référence : `commands.md`, Recon / Extraction.

## 3. Binary-to-source translation (source reconstruction)
- **Boucle main :** fgets(buffer), puis selon l’entrée : "auth " → malloc(4) pour **auth**, strcpy(auth, input+5) si strlen(input+5) ≤ 30. "reset" → free(auth). "service" → strdup(input+7) → **service**. "login" → si **(auth+0x20) != 0** alors system("/bin/sh"), sinon "Password:".
- **Où ça peut casser :** auth ne fait que 4 octets ; strcpy peut en écrire jusqu’à 30 → overflow, mais auth+0x20 = 32, on n’atteint pas 32 avec le seul overflow. En revanche **(auth+0x20)** est lu **dans le heap** : c’est l’adresse auth+32. Si une allocation **service** (strdup) est placée juste après auth, auth+0x20 peut tomber **dans** le buffer de service. En envoyant "service" + une longue chaîne, strdup remplit ce buffer et met un octet non nul à auth+0x20.
- Source : voir `source.c` / `source.md`.

## 4. Understanding where it can break (vulnerability hypothesis)
- **Comportement :** login lit *(auth+0x20) comme « flag » d’authentification. auth = 4 octets ; auth+0x20 est au-delà du bloc auth, dans le heap.
- **Succès :** *(auth+0x20) != 0 au moment de login. On n’écrase pas une adresse de retour ; on remplit une **zone heap** qui correspond à auth+0x20 via l’allocation service.
- **Hypothèse :** après "auth AAAA", une allocation "service" + longue chaîne place un bloc juste après auth ; auth+0x20 tombe dans ce bloc. La longueur minimale (21, 32, etc.) à confirmer en GDB.

## 5. GDB diagnosis step-by-step

1. **Lancer GDB**  
   ```bash
   gdb -q ./level8.bin
   ```

2. **Repérer login et la lecture *(auth+0x20)**  
   ```gdb
   disas login
   ```  
   Ou chercher la comparaison avec 0 (auth+0x20). Noter l’instruction qui charge *(auth+0x20). Mettre un breakpoint à l’entrée de login.

3. **Breakpoint dans login**  
   ```gdb
   break login
   run
   ```  
   Dans le terminal du programme : taper `auth AAAA` puis `service` + 32×'A' puis `login`. Quand on atteint le breakpoint :  
   ```gdb
   p/x auth
   p/x *(auth+0x20)
   ```  
   auth est l’adresse du bloc (ex. 0x0804a008). auth+0x20 = auth+32. Vérifier que la **valeur** lue à *(auth+0x20) est non nulle (ex. 0x41). Cela prouve que la zone auth+0x20 a été remplie par le buffer service.

4. **Vérifier le layout heap**  
   Après "auth AAAA" puis "service" + 32×'A' :  
   ```gdb
   x/32bx auth
   ```  
   Puis noter l’adresse du bloc service (variable globale ou retour de strdup). Confirmer que auth+0x20 (auth+32) tombe à l’intérieur du bloc service (en-têtes + données). Si avec 21 octets après "service" ça ne suffit pas, réessayer avec 32.

5. **Nombre d’octets après "service"**  
   Tester 21, 32, 40. Sur beaucoup de VM **32** est sûr. La valeur n’est pas une adresse en little-endian ; c’est simplement la longueur de la chaîne pour que strdup alloue un bloc dont la zone utilisée recouvre auth+0x20.

## 6. Exploit design and command explanation

**Génération de la commande (converter.py) :**  
`level8/converter.py` affiche la séquence (auth / service + padding / login) et la commande en pipe. Le nombre de 'A' après « service » (32 par défaut) est configurable si le layout heap change.

**Conception :** Pas d’écrasement d’adresse de retour. Le programme lit *(auth+0x20) ; cette adresse est dans le heap après le bloc auth. Une allocation **service** (strdup) peut être adjacente à auth ; auth+0x20 tombe alors dans le buffer service. En envoyant une longue chaîne après "service", on met un octet non nul à cet offset ; login donne le shell.

**Commande / séquence (voir `commands.md`, Exploitation) :**
```bash
./level8
# Puis taper :
auth AAAA
service AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
login
```
Ou en une ligne (stdin peut se fermer avant le shell selon l’implémentation) :
```bash
(echo "auth AAAA"; echo "service AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"; echo "login") | ./level8
```

**Décomposition :**

- **Pas de payload binaire en little-endian** ; tout est du texte.

- **Étape 1 — "auth AAAA"**  
  Alloue le bloc auth (4 octets). "AAAA" (4 octets) évite un reset et garde une entrée courte. Le bloc auth a une adresse fixe (ex. 0x0804a008).

- **Étape 2 — "service" + 32×'A'**  
  strdup("AAAAAAAA...") (32 caractères) alloue un bloc sur le heap. Sur l’allocateur Rainfall ce bloc est souvent juste après auth. Les 32 octets remplissent la zone utilisable ; avec les en-têtes, **auth+0x20** (auth+32) tombe dans cette zone et reçoit un 'A' (0x41) → *(auth+0x20) != 0.

- **Étape 3 — "login"**  
  Le programme lit *(auth+0x20) ; c’est non nul → system("/bin/sh") est appelé.

Résumé : on n’écrase pas de pointeur ; on **remplit** la zone heap à auth+0x20 en profitant du layout (service après auth). Les "A" ne sont pas une adresse ; c’est la longueur (32) qui compte pour recouvrir auth+0x20.

## 7. Reproducible procedure (for evaluation)
- **Commande :** lancer `./level8`, taper `auth AAAA`, puis `service AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`, puis `login`. Dans le shell : `cat /home/user/level9/.pass`.
- **Résultat attendu :** shell level9.
- **À dire :** « auth ne fait que 4 octets mais login lit à auth+0x20. Cette zone est dans le heap après auth. En allouant service avec une longue chaîne, auth+0x20 tombe dans le buffer service et est rempli ; login voit un octet non nul et lance le shell. »

## 8. Oral defense points
- **Bug :** strcpy(auth, input+5) avec auth = 4 octets (overflow) ; surtout login lit *(auth+0x20) qui peut être dans une autre allocation (service). Conception fragile.
- **GDB :** confirme que le bloc service est adjacent à auth et que *(auth+0x20) est non nul après "service" + 32×'A'.
- **Payload :** auth court + service + longue chaîne + login (pas d’adresse en LE).
- **Fix :** ne pas lire auth+0x20 sans l’avoir défini ; utiliser un flag séparé ou allouer auth avec une taille cohérente.

## 9. Common evaluator questions
- **Pourquoi auth+0x20 ?** Le programme utilise cet offset comme « flag » ; auth ne fait que 4 octets.
- **Pourquoi service ?** strdup(service) alloue un bloc souvent juste après auth, donc auth+0x20 tombe dans ce bloc.
- **Combien d’octets après service ?** Au moins 21 ; souvent 32 pour être sûr (trouvé en GDB ou par essai).
- **Pas de little-endian ?** Correct : l’exploit ne contient pas d’adresse à écrire ; on remplit une zone avec des caractères non nuls.
