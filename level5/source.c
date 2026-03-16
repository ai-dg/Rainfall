/*
 * Reconstruction level5 (Rainfall).
 * n() : printf(buffer) puis exit(1). o() : system("/bin/sh"). Jamais appelée.
 * Exploit : écraser la GOT de exit par l'adresse de o.
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void o(void)
{
	system("/bin/sh");
	_exit(1);
}

void n(void)
{
	char buf[512];

	fgets(buf, 512, stdin);
	printf(buf);  /* format string */
	exit(1);      /* GOT à 0x8049838 → remplacer par &o */
}

int main(void)
{
	n();
	return 0;
}
