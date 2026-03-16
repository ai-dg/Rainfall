# Level8 — Walkthrough

## 1. Objectif

Obtenir un shell level9. Le binaire propose **auth**, **reset**, **service**, **login**. **login** exécute **system("/bin/sh")** si l’octet à **auth+0x20** est non nul.

## 2. Inspection

- **auth** : malloc(4), puis strcpy(auth, input+5) si longueur ≤ 30 → overflow possible.
- **service** : strdup(input+7) → nouvelle allocation heap.
- **login** : si **(auth+0x20) != 0** → system("/bin/sh").

## 3. Vulnérabilité

- **auth** ne fait que 4 octets ; on ne peut pas atteindre auth+0x20 (32) avec le seul overflow de **auth** (max 30 octets copiés).
- L’octet à **auth+0x20** est lu dans le heap. Si **service** (strdup) est alloué juste après auth, auth+0x20 peut être **dans** le buffer service. Une longue chaîne après **service** remplit ce buffer et met un octet non nul à cet offset.

## 4. Exploit

1. **auth AAAA** → allocation de auth.
2. **service** + longue chaîne (≥ 21–32 octets) → strdup alloue après auth ; auth+0x20 tombe dans ce buffer.
3. **login** → *(auth+0x20) ≠ 0 → shell.

## 5. Récupération du mot de passe

Dans le shell : `cat /home/user/level9/.pass`. Consigner dans `level8/flag`.
