# Level8 - Exam Notes

## 1. Objective
Obtenir un shell level9. Commandes : **auth**, **reset**, **service**, **login**. **login** exécute `system("/bin/sh")` si l’octet à **(auth+0x20)** est non nul.

## 2. Initial diagnosis (before GDB)
- **Comportement :** auth fait malloc(4), strcpy(auth, input+5) si strlen ≤ 30 → overflow (30 octets dans 4), mais auth+0x20 = 32, donc on n’atteint pas auth+0x20 avec le seul overflow de auth. **login** lit *(auth+0x20) ; si non nul → shell.
- **Idée :** auth+0x20 est une adresse **dans le heap** après le bloc auth. Si **service** (strdup) alloue juste après auth, auth+0x20 peut tomber **dans** le buffer de service. En envoyant "service" + une longue chaîne, strdup remplit ce buffer et écrit un octet non nul à auth+0x20.
- **Hypothèse :** exploitation du layout heap ; pas d’écrasement d’adresse de retour, mais remplissage d’une zone lue par login à offset fixe (auth+0x20).

## 3. GDB diagnosis (how the vulnerability was found)
- **Où break :** à l’entrée de login, sur l’instruction qui charge *(auth+0x20). But : voir l’adresse lue et la valeur ; confirmer que cette adresse tombe dans le bloc service après "auth AAAA" puis "service" + N octets.
- **Layout heap :** après "auth AAAA", noter l’adresse de auth (ex. 0x0804a008). auth+0x20 = auth+32. Ensuite "service" + 21×'A' (ou 32) : strdup alloue un bloc. Vérifier avec `x/32bx auth` et l’adresse du bloc service que auth+0x20 tombe à l’intérieur du buffer service (en-têtes + données). Sur beaucoup de VM, 21 octets suffisent ; sur d’autres il faut 32 ou plus.
- **Offset / taille :** pas d’offset classique ; il s’agit de la **longueur** de la chaîne après "service" pour que les octets écrits par strdup recouvrent auth+0x20. Tester 21, 32, 40 jusqu’à ce que login ouvre le shell.
- **Contrôle du flux :** à login, *(auth+0x20) doit être non nul. Après "auth AAAA" + "service" + 32×'A', inspecter *(auth+0x20) en GDB : doit valoir 0x41 (ou un autre non-nul). Cela prouve que auth+0x20 est bien dans le buffer service.

## 4. Building the exploit command
- **Cible :** faire en sorte que *(auth+0x20) soit non nul au moment de login. On ne modifie pas directement auth ; on remplit la zone heap qui correspond à auth+0x20 via l’allocation service.
- **Structure :** pas de payload binaire ; séquence de commandes. 1) "auth AAAA" (ou court) pour allouer auth sans reset. 2) "service" + une chaîne d’au moins 21 octets (souvent 32 pour être sûr). 3) "login". La chaîne après "service" est copiée par strdup ; elle remplit le bloc qui peut recouvrir auth+0x20.
- **Encodage :** aucune ; entrée texte. Ex. `echo -e "auth AAAA\nservice AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nlogin\n"` ou taper à la main.
- **Invocation :** `./level8` puis envoyer les trois lignes (ou pipe depuis un fichier / echo -e).
- **Référence commands.md :** section Exploitation. La longueur (21 ou 32) peut varier selon la VM ; la trouver en GDB ou par essai.

## 5. Exploitation logic
Le programme lit *(auth+0x20) comme « flag » d’authentification. auth ne fait que 4 octets ; auth+0x20 est dans le heap après auth. Une allocation service (strdup) peut être placée juste après auth ; auth+0x20 tombe alors dans le buffer service. En envoyant une longue chaîne après "service", on met un octet non nul à auth+0x20 ; login donne le shell.

## 6. Reproducible procedure (for evaluation)
- **Commande :** `./level8`, puis taper : `auth AAAA`, `service AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA`, `login`. Ou : `(echo "auth AAAA"; echo "service AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"; echo "login") | ./level8` (stdin peut se fermer avant d’utiliser le shell selon l’implémentation ; sinon entrée interactive).
- **Résultat attendu :** shell level9. Puis `cat /home/user/level9/.pass`.
- **À dire :** « auth ne fait que 4 octets mais login lit à auth+0x20. Cette zone est dans le heap après auth. En allouant service avec une longue chaîne, auth+0x20 tombe dans le buffer service et est rempli ; login voit un octet non nul et lance le shell. »

## 7. Oral defense points
- **Bug :** strcpy(auth, input+5) avec auth = 4 octets (overflow) ; surtout login lit *(auth+0x20) qui peut être dans une autre allocation (service). Conception fragile.
- **GDB :** confirme que le bloc service est adjacent à auth et que auth+0x20 tombe dans le buffer service ; confirme la valeur lue à login.
- **Payload :** auth court + service + longue chaîne + login.
- **Fix :** ne pas lire auth+0x20 sans l’avoir défini ; utiliser un flag séparé ou allouer auth avec une taille cohérente.

## 8. Common evaluator questions
- **Pourquoi auth+0x20 ?** Le programme utilise cet offset comme « flag » d’authentification ; auth ne fait que 4 octets, donc c’est une mauvaise conception.
- **Pourquoi service ?** strdup(service) alloue un bloc ; il est souvent placé juste après auth, donc auth+0x20 tombe dans ce bloc.
- **Combien d’octets après service ?** Au moins 21 ; selon la VM et les en-têtes malloc, 32 ou plus.
- **Overflow classique ?** Il y a un overflow sur auth (30 octets dans 4), mais on n’atteint pas 32 ; l’exploit repose sur une autre allocation (service) qui recouvre auth+0x20.
