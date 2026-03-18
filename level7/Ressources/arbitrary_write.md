# Arbitrary write (écriture arbitraire)

## Concept
Une **arbitrary write** permet d’écrire une **valeur** à une **adresse** de notre choix. Ici on l’obtient en contrôlant la **destination** d’un `strcpy` via un premier overflow.

## Définition simple
- Premier `strcpy(dest1, argv[1])` : pas de borne, on peut dépasser `dest1` et écraser d’autres variables (ex. `dest2`).
- Si `dest2` est utilisé comme **destination** du second `strcpy(dest2, argv[2])`, alors on choisit **où** argv[2] est copié : on met l’adresse cible dans argv[1], la valeur dans argv[2].

## Où ça apparaît (level7)
- Deux structures : ptr1 (bloc 8 octets), ptr2 (bloc 8 octets). Chacune a un champ pointeur vers un buffer.
- `strcpy(ptr1[1], argv[1])` puis `strcpy(ptr2[1], argv[2])`.
- En overflowant le premier buffer, on écrase **ptr2[1]** (la destination du 2ᵉ strcpy).
- On met **GOT de puts** dans argv[1] (à l’offset qui écrase ptr2[1]), et **adresse de m** dans argv[2] → le 2ᵉ strcpy écrit l’adresse de m dans la GOT.

## Schéma

```
  argv[1] = [padding 20 octets][adresse GOT puts]
              ↓ overflow
  ptr1[1] remplit son bloc, puis écrase ptr2[0], ptr2[1]
  ptr2[1] = adresse GOT puts  →  strcpy(GOT_puts, argv[2])
  argv[2] = adresse de m (4 octets)  →  écrit à GOT puts
```

## Utilité en exploitation
- Un seul “gadget” : **écriture d’une valeur à une adresse choisie**.
- Cible = entrée GOT (puts) ; valeur = adresse de la fonction qu’on veut appeler à la place (m).

## Exemple level7
- Offset vers ptr2[1] : **20** octets (8 + 8 + 4 selon le layout).
- argv[1] = `"A"*20 + "\x28\x99\x04\x08"` (GOT puts 0x8049928).
- argv[2] = `"\xf4\x84\x04\x08"` (m = 0x080484f4).
- Résultat : `puts("~~")` appelle m() qui affiche le buffer contenant le mot de passe.

## Résumé mental
Arbitrary write = contrôler à la fois l’adresse d’écriture et la valeur. Ici : overflow pour contrôler la destination du 2ᵉ strcpy, puis écrire dans la GOT.

## Références
- `strcpy(3)` (absence de borne / copie jusqu’au `\0`) : https://man7.org/linux/man-pages/man3/strcpy.3.html
