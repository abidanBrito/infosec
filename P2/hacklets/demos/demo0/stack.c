#include <stdio.h>

void foo()
{
    // do something
    char buffer[12];

    for (int i = 0; i < 12; i++)
    {
        buffer[i] = 'a' + i;
    }
    buffer[11] = '\0';

    printf("Buffer content: %s\n", buffer);
}

int main()
{
    int volatile local = 0xDEADBEEF;
    foo();
    return 0;
}