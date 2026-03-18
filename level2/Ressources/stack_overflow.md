# Buffer overflow et contrainte sur ret (level2)

## Concept
Même idée que level1 (overflow via gets), mais le binaire **refuse** que l’adresse de retour soit dans la plage 0xb0000000–0xbfffffff (stack). Un test du type `(ret & 0xb0000000) == 0xb0000000` provoque un exit si on retourne directement vers le buffer (shellcode).

## Définition simple
- On ne peut pas mettre l’adresse du buffer (0xb...) en adresse de retour.
- **Solution :** retourner vers un **gadget** dans le binaire (ex. `pop; ret`). Le gadget consomme un ou deux mots de la stack ; on y met l’adresse du buffer. Le `ret` du gadget saute alors vers le buffer → exécution du shellcode.

## Où ça apparaît (level2)
- Fonction `p()` : gets(buffer), buffer à ebp-0x4c. **Offset** jusqu’à ret = 80 octets.
- Gadget typique : **0x08048385** (`pop ebx; ret`). En retournant ici : pop consomme le 1er mot (adresse buffer), ret saute au 2e mot (encore adresse buffer) → shellcode.

## Résumé mental
Contrainte sur ret → on utilise un gadget en .text pour faire un second saut vers la stack (buffer).

## Références
- `gets(3)` : https://man7.org/linux/man-pages/man3/gets.3.html
