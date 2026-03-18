# Shellcode (level9)

## Concept
Un **shellcode** est du code machine injecté (souvent un petit exécutable qui lance un shell, ex. execve("/bin/sh")). Comme le binaire level9 n’a pas `system` ni "/bin/sh", on doit exécuter notre propre code.

## Définition simple
- Suite d’octets = instructions x86 (éviter les NULL pour pouvoir être dans une chaîne).
- Classique : **execve("/bin/sh", NULL, NULL)** (appel système 0x0b sur i386).
- On le place dans l’**environnement** (variable payload=...) pour avoir une adresse stable (sans ASLR sur la VM).

## Où ça apparaît (level9)
- L’appel virtuel saute vers *(second->vptr) = *(premier+4). On met à **premier+4** l’adresse du shellcode (4 premiers octets du payload).
- Le shellcode est dans **env** : `env -i payload=$(python -c 'print "\x90"*1000 + "<shellcode>"')`.
- Nopsled (1000×\x90) pour faciliter l’atteinte de l’adresse ; l’adresse exacte (ex. 0xbffffc63) se trouve en GDB avec `x/200s environ`.

## Flux

```
  call edx   (edx = *(premier+4) = adresse shellcode)
      ↓
  nopsled → shellcode execve("/bin/sh")
      ↓
  shell
```

## Exemple (shellcode i386 classique)
- Octets : `\xeb\x1f\x5e\x89\x76\x08\x31\xc0\x88\x46\x07...` + "/bin/sh".
- Utilisé dans la variable d’environnement ; adresse trouvée en GDB (ex. 0xbffffc63) → mise en little-endian au début du payload argv[1].

## Résumé mental
Pas de gadget “system” dans le binaire → on injecte du code (shellcode) dans l’env et on détourne l’appel virtuel vers cette adresse.

## Références
- `execve(2)` (l’appel système pour lancer un binaire) : https://man7.org/linux/man-pages/man2/execve.2.html
