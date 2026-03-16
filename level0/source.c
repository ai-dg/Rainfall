/*
 * Reconstruction du binaire level0 (Rainfall).
 * Logique : si argv[1] == 423 (0x1a7), lance /bin/sh avec euid/egid effectifs (setuid).
 */

#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#define MAGIC 0x1a7  /* 423 */

int main(int argc, char **argv)
{
	if (argc < 2)
		goto fail;

	if (atoi(argv[1]) != MAGIC)
		goto fail;

	char *sh = strdup("/bin/sh");
	gid_t egid = getegid();
	uid_t euid = geteuid();

	setresgid(egid, egid, egid);
	setresuid(euid, euid, euid);

	execv("/bin/sh", (char *[]){ sh, NULL });
	/* unreachable si execv réussit */
	return 0;

fail:
	fwrite("No !\n", 1, 5, stderr);
	return 1;
}
