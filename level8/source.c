/*
 * Reconstruction level8 (Rainfall).
 * Boucle : auth (malloc(4) + strcpy sans vraie limite), reset (free auth),
 * service (strdup), login (si *(auth+0x20) != 0 → system("/bin/sh")).
 * Exploit : auth court, puis service avec longue chaîne pour que auth+0x20
 * tombe dans le buffer service.
 */

#include <stdlib.h>
#include <stdio.h>
#include <string.h>

static char *auth;
static char *service;

int main(void)
{
	char buf[0x80];

	while (1) {
		printf("%p, %p \n", auth, service);
		if (!fgets(buf, 0x80, stdin))
			break;
		if (strncmp(buf, "auth ", 5) == 0) {
			auth = malloc(4);
			*auth = 0;
			if (strlen(buf + 5) <= 0x1e)
				strcpy(auth, buf + 5);  /* overflow */
		} else if (strncmp(buf, "reset", 5) == 0) {
			free(auth);
		} else if (strncmp(buf, "service", 6) == 0) {
			service = strdup(buf + 7);
		} else if (strncmp(buf, "login", 5) == 0) {
			if (*(auth + 0x20))
				system("/bin/sh");
			else
				fwrite("Password:\n", 1, 10, stdout);
			break;
		}
	}
	return 0;
}
