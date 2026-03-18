# Level0 - Exam Notes

## 1. Objective
Obtenir un shell avec les privilèges level1 pour lire le mot de passe level1. Le binaire est setuid level1.

## 2. Initial diagnosis (before GDB)
- **Fonctions suspectes :** pas de gets/strcpy ; `main` prend un argument, appelle `atoi`. Comparaison avec une constante visible en désassemblage.
- **Entrée utilisateur :** `argv[1]` converti en entier ; pas de lecture non bornée.
- **Succès :** exécution de `/bin/sh` avec euid level1 (setresuid puis execv).
- **Hypothèse :** pas d’overflow ; condition secrète (backdoor) — une valeur d’argument déclenche la branche « shell ».

## 3. GDB diagnosis (how the vulnerability was found)
Pas de corruption mémoire ; le diagnostic repose sur l’analyse statique (objdump/readelf) plus une vérification optionnelle en GDB.

- **Où break :** après l’appel à `atoi` dans main (ou avant la comparaison). But : confirmer que l’argument est bien dans eax et voir la constante comparée.
- **Layout :** inutile (pas d’overflow). En GDB : `b *main+<offset_cmp>`, `r 423`, vérifier `cmp $0x1a7,%eax` dans le désassemblage.
- **Valeur attendue :** dans le désassemblage de main, recherche de la comparaison après atoi → `cmp $0x1a7,%eax`. Donc la valeur qui fait passer le test est **0x1a7** = **423** en décimal.
- **Contrôle du flux :** si égalité, le flux va vers la branche qui fait setresuid/setresgid puis execv("/bin/sh", ...). Adresse de la chaîne "/bin/sh" en .rodata (ex. 0x80c5348) pour confirmer.

## 4. Building the exploit command
- **Cible :** faire en sorte que la comparaison soit vraie (eax == 0x1a7) en passant la bonne valeur en argument.
- **Payload :** un seul argument entier : **423** (pas de padding ni d’octets bruts).
- **Encodage :** aucun ; argument ASCII "423".
- **Invocation :** `./level0 423` — le programme lit argv[1], atoi("423") = 423 = 0x1a7 → branche shell.
- **Référence commands.md :** la commande finale est dans `commands.md` (section Exploitation / procédure). Commande de démo : `./level0 423`.

## 5. Exploitation logic
Pas d’exploit mémoire : backdoor. Le binaire compare atoi(argv[1]) à 0x1a7 ; si égal, il lance /bin/sh avec les droits level1. Fournir 423 suffit.

## 6. Reproducible procedure (for evaluation)
- **Commande :** `./level0 423` puis dans le shell : `id`, `cat /home/user/level1/.pass` (ou chemin indiqué par le sujet).
- **Résultat attendu :** shell avec euid level1, mot de passe affiché.
- **À dire :** « Le binaire compare l’argument à 0x1a7. J’ai trouvé cette valeur en désassemblant main. Je lance avec 423 pour déclencher execv("/bin/sh"). »

## 7. Oral defense points
- **Bug :** condition secrète (backdoor) : comparaison avec 0x1a7 après atoi(argv[1]).
- **Où :** dans main, après l’appel à atoi.
- **GDB / analyse :** désassemblage confirme `cmp $0x1a7,%eax` ; pas d’offset stack.
- **Payload :** argument 423.
- **Fix :** supprimer la backdoor ou ne pas exposer ce binaire setuid avec cette logique.

## 8. Common evaluator questions
- **Pourquoi 423 ?** 0x1a7 en décimal = 423 ; c’est la valeur comparée dans le binaire.
- **Où as-tu trouvé cette valeur ?** Dans le désassemblage de main : `cmp $0x1a7,%eax` (objdump -d).
- **Y a-t-il un overflow ?** Non ; la vulnérabilité est une backdoor.
- **Comment obtenir le shell ?** Le binaire est setuid ; en passant le test, il fait setresuid puis execv("/bin/sh").
