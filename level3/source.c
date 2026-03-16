/*
 * Reconstruction level3 (Rainfall).
 * Vulnérabilité : printf(buffer) → format string. Variable m doit valoir 64 pour system("/bin/sh").
 */

#include <stdio.h>

int m;  /* global, adresse 0x804988c */

void v(void)
{
	char buf[512];

	fgets(buf, 512, stdin);
	printf(buf);  /* format string : entrée contrôlée */
	if (m == 0x40) {
		fwrite("Wait what?!\n", 1, 12, stdout);
		system("/bin/sh");
	}
}

int main(void)
{
	v();
	return 0;
}
