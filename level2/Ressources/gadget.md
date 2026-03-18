# Gadget (ROP / second saut)

## Concept
Un **gadget** est une courte séquence d’instructions déjà présente dans le binaire (ex. `pop reg; ret`). En plaçant cette adresse en adresse de retour, on « consomme » des mots sur la stack puis on saute vers l’adresse suivante (qu’on contrôle).

## Définition simple
- Ex. `pop ebx; ret` : pop lit 4 octets (notre adresse buffer), ret lit les 4 suivants (encore l’adresse buffer) et saute → exécution du code au début du buffer.

## Où ça apparaît (level2)
- **0x08048385** : `pop ebx; ret`. Payload : [shellcode][padding][0x08048385][addr_buf][addr_buf]. Au ret de p → gadget ; après pop+ret → buffer (shellcode).

## Résumé mental
Gadget = petit bout de code existant pour rediriger le flux (ici : sauter au buffer malgré la contrainte 0xb...).

## Références
- Recherche de gadgets : `objdump -d level2 | grep -A1 pop`
