#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void)
{
    int x;
    printf("Hello%n\n", &x);
    printf("x: %d\n", x);
    int number = printf("%123x");
    printf("number: %d\n", number);
    printf("AAAA%134x%2$n\n", 0, &x);
    printf("x: %d\n", x);
    return 0;
}