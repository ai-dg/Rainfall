/*
 * Reconstruction level2 (Rainfall).
 * p() : gets(buffer) puis vérifie que l'adresse de retour n'est pas sur la stack (0xb0...).
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void p(void)
{
	char buf[76];  /* ebp-0x4c */
	unsigned int ret;

	fflush(stdout);
	gets(buf);
	ret = *(unsigned int *)((char *)&ret + 20);  /* simplified: saved EIP */
	if ((ret & 0xb0000000) == 0xb0000000) {
		printf("(%p)\n", (void *)ret);
		_exit(1);
	}
	puts(buf);
	strdup(buf);
}

int main(void)
{
	p();
	return 0;
}
