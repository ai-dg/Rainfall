#include <stdio.h>
#include <stdlib.h>

int main(void)
{
    char *p = getenv("payload");
    printf("payload at: %p\n", p);
    return 0;
}
