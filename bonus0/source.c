/*
 * Reconstruction bonus0 (Rainfall) — depuis le binaire.
 * Lit deux lignes sur stdin, concatène dans un buffer de 42 octets → overflow.
 */

#include <unistd.h>
#include <string.h>
#include <stdio.h>

#define PROMPT " - "
#define BUF1_SIZE 20
#define BUF2_SIZE 20

static void p(char *dest, const char *prompt)
{
	char buf[0x1000];

	puts(prompt);
	read(0, buf, 0x1000);
	*(strchr(buf, '\n')) = '\0';
	strncpy(dest, buf, BUF1_SIZE);  /* 20 octets max */
}

static void pp(char *dest)
{
	char buf1[BUF1_SIZE];   /* ebp-0x30, 20 octets */
	char buf2[BUF2_SIZE];   /* ebp-0x1c, 20 octets */

	p(buf1, PROMPT);
	p(buf2, PROMPT);
	strcpy(dest, buf1);           /* pas de limite */
	dest[strlen(dest)] = ' ';     /* espace (rodata 0x80486a4) */
	dest[strlen(dest) + 1] = '\0';
	strcat(dest, buf2);           /* 20+2+20 = 42 octets → overflow 1 si buffer=42 */
}

int main(void)
{
	char buffer[42];   /* main : esp+0x16, 0x40-0x16 = 42 octets */

	pp(buffer);
	puts(buffer);
	return 0;
}
