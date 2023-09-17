#include <stdio.h>

int main()
{
    char buffer[32] = {0};
    fgets(buffer, 32, stdin);
    printf("%s\n", buffer);
    return 0;
}