/*
 * Reconstruction level6 (Rainfall).
 * main : strcpy(buffer, argv[1]) sans limite ; call *fn_ptr.
 * n() exécute system("/bin/cat /home/user/level7/.pass"). Exploit : overflow + écraser fn_ptr par &n.
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

void n(void)
{
	system("/bin/cat /home/user/level7/.pass");
}

void m(void)
{
	puts("Nope");
}

int main(int argc, char **argv)
{
	char  *buf;
	void **fn_ptr;  /* pointeur vers 4 octets contenant l’adresse de fonction */

	buf = malloc(0x40);
	fn_ptr = (void **)malloc(4);
	*fn_ptr = (void *)m;
	strcpy(buf, argv[1]);   /* overflow : pas de limite */
	((void (*)(void))*fn_ptr)();
	return 0;
}
