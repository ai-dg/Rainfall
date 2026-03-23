#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

int main(void)
{
    int x=10;

    printf("address x: %p\n", &x);

    printf("123456789%n\n", &x);



    printf("x: %d\n", x);



    
    int number = printf("%20xPierina\n");
    // printf("number: %d\n", number);
    // printf("AAAA%134x%2$n\n", 0, &x);
    // printf("x: %d\n", x);
    // return 0;
}