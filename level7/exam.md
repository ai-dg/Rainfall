# Level7 - Exam Notes

## 1. Objective
Afficher le mot de passe level8. Le programme lit le mot de passe dans un buffer global **c** puis appelle puts("~~"). Il faut détourner un appel pour afficher **c** (ex. en remplaçant l’entrée GOT de puts par l’adresse de **m** qui fait printf avec c).

## 2. Initial diagnosis (before GDB)
- **Fonctions suspectes :** deux `strcpy` : strcpy(ptr1[1], argv[1]) et strcpy(ptr2[1], argv[2]) sans limite. ptr1[1] et ptr2[1] pointent vers des blocs de 8 octets. Layout heap : [bloc1][bloc2][bloc3][bloc4]. En dépassant 8 octets dans bloc2 (ptr1[1]), on écrase bloc3 = **ptr2[0]** et **ptr2[1]** (destination du 2e strcpy). Donc on contrôle **où** argv[2] est écrit (arbitrary write).
- **Entrée utilisateur :** argv[1] et argv[2].
- **Succès :** faire afficher le buffer c (où fgets a lu le mot de passe). **m()** (0x80484f4) fait printf avec c. En écrasant la **GOT de puts** (0x8049928) par l’adresse de m, l’appel à puts("~~") exécutera m() → affichage de c.
- **Hypothèse :** overflow argv[1] pour mettre ptr2[1] = GOT puts ; argv[2] = adresse de m. Le 2e strcpy écrit alors m dans la GOT.

## 3. GDB diagnosis (how the vulnerability was found)
- **Où break :** après les deux strcpy, avant fopen/puts. But : vérifier que ptr2[1] pointe vers 0x8049928 et que la GOT contient 0x080484f4.
- **Layout heap :** ptr1 = malloc(8), ptr1[1] = malloc(8) (bloc2) ; ptr2 = malloc(8), ptr2[1] = malloc(8) (bloc4). Bloc2 fait 8 octets (ou plus avec en-tête). En écrivant 20 octets dans bloc2 (argv[1] = 20 octets + 4 octets adresse), on écrase le début de bloc3 : ptr2[0] et ptr2[1]. Les 4 derniers octets de argv[1] deviennent la nouvelle valeur de ptr2[1]. Donc argv[1] = [20 octets] + [0x8049928] pour que ptr2[1] = GOT puts. **Offset 20** sur Rainfall (à confirmer : 8+8+padding).
- **Adresses :** GOT puts : `readelf -r` ou `x/wx` après résolution → **0x8049928**. m : **0x080484f4**.
- **Contrôle du flux :** après les strcpy, strcpy(ptr2[1], argv[2]) écrit argv[2] à 0x8049928. Si argv[2] = "\xf4\x84\x04\x08", la GOT contient 0x080484f4. Au call puts, le programme saute vers m() qui affiche c. Vérifier : `x/wx 0x8049928` après exploit = 0x080484f4.

## 4. Building the exploit command
- **Cible :** ptr2[1] (destination du 2e strcpy) = GOT puts = 0x8049928 ; contenu à écrire à cette adresse = adresse de m = 0x080484f4 (argv[2]).
- **Structure :** argv[1] = [20 octets padding] + [\x28\x99\x04\x08] (4 octets). argv[2] = [\xf4\x84\x04\x08] (4 octets + \0 par strcpy). Les 20 octets remplissent bloc2 et écrasent ptr2[0]/ptr2[1] ; les 4 derniers octets de argv[1] = nouvelle ptr2[1] = GOT.
- **Encodage :** adresses en LE. Python : argv[1] `"A"*20 + "\x28\x99\x04\x08"`, argv[2] `"\xf4\x84\x04\x08"`.
- **Invocation :** `./level7 "$(python -c '...')" "$(python -c '...')"`.
- **Référence commands.md :** section Exploitation. Offset 20 et adresses GOT/m viennent du diagnostic GDB.

## 5. Exploitation logic
Arbitrary write : en overflowant ptr1[1], on écrase ptr2[1]. Le 2e strcpy écrit argv[2] à l’adresse qu’on a mise dans ptr2[1] (GOT puts). On y écrit l’adresse de m ; puts("~~") appelle alors m() qui affiche le buffer c (mot de passe).

## 6. Reproducible procedure (for evaluation)
- **Commande :** `./level7 $(python -c 'print "A"*20 + "\x28\x99\x04\x08"') $(python -c 'print "\xf4\x84\x04\x08"')`. Sortie : "(mot de passe) - (timestamp)".
- **Résultat attendu :** le mot de passe level8 s’affiche (avec un timestamp).
- **À dire :** « Le premier strcpy overflow et écrase ptr2[1]. Je mets la GOT de puts dans ptr2[1] et l’adresse de m dans argv[2]. Le second strcpy écrit m dans la GOT ; puts appelle alors m() qui affiche c. »

## 7. Oral defense points
- **Bug :** strcpy(ptr1[1], argv[1]) sans limite ; en dépassant 8 octets on écrase ptr2[1], donc la destination du 2e strcpy.
- **GDB :** offset 20, GOT puts 0x8049928, m 0x080484f4 ; après exploit la GOT contient l’adresse de m.
- **Payload :** argv[1] = padding + GOT puts ; argv[2] = adresse de m.
- **Fix :** borner les strcpy (strncpy) ; ne pas faire dépendre la sécurité de l’ordre des allocations.

## 8. Common evaluator questions
- **Pourquoi la GOT de puts ?** Le programme appelle puts("~~") après avoir lu le mot de passe dans c ; en remplaçant cette entrée par m(), l’appel affiche c.
- **Pourquoi 20 octets ?** Taille du bloc ptr1[1] (8) + champ ptr2[0] (4) + padding pour que les 4 derniers octets de argv[1] écrasent ptr2[1]. Valeur trouvée en GDB sur Rainfall.
- **Où est le mot de passe ?** Lu par fgets dans le buffer global c (0x8049960).
- **Arbitrary write ?** Oui : on choisit l’adresse (ptr2[1]) où strcpy écrit argv[2].
