#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/types.h>
#include <sys/stat.h>
const int sbox[16] = {0, 2, 0, 1, 7, 3, 4, 5, 11, 12, 15, 6, 7, 14, 10, 3};

// Secret derivation function, only the correct
// seed and iteration count will lead to the correct password
unsigned int derive_password(int seed, int count)
{
    srand(seed);
    unsigned int temp = rand();
    for(int i = 0; i < count; i++)
    {
        int shuffle = rand() % 16;
        unsigned int x = temp & ((1<<shuffle)-1);
        temp = (temp >> shuffle) | (x << (sizeof(int)*8-shuffle));
        unsigned int y = temp & 0b1111;
        temp = (temp & ~0b1111) | sbox[y]; 
        //printf("%x\n",temp);
    }
    return temp;
}

int main()
{
    int x, y;
    printf("Give me the password seed\n");
    fflush(stdout);
    scanf("%d", &x);
    printf("And now the iteration count\n");
    fflush(stdout);
    scanf("%d", &y);
    printf("Enter the file name:\n");
    fflush(stdout);
    char buffer[256];
    scanf("%256s", buffer);
    if(strstr(buffer, "flag"))
    {
        printf("Not so fast!\n");
        exit(1);
    }
    struct stat buf;
    int c;

    c = lstat(buffer, &buf);
    if(c == -1)
    {
        printf("The file does not exist!\n");
        return 0;
    }
    if (S_ISLNK(buf.st_mode))
    {
        printf("Sneaky, but not good enough!\n");
        return 0;
    }    
    unsigned int pw = derive_password(x, y);
    printf("pw: %ud", pw);
    if(!pw)
    {
        printf("Well done, here is your file: ");
        FILE *f = fopen(buffer, "r");
        char buf[128];
        memset(buf, 0, sizeof(buf));
        fread(&buf, 1, sizeof(buf) - 1, f);
        printf("%s", buf);
        fflush(stdout);
    }
    printf("Bye");
}