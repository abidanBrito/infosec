#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/random.h>

#include <faultconfig.h>

#define PW_LEN 16


int constant_time_strcmp(char *string1, char *string2, size_t len)
{
    char diff = 0;
    for (size_t i = 0; i < len; i++)
    {
        diff |= string1[i] ^ string2[i];
        printf("Click. ");
    }
    puts("");

    return diff;
}


int main(int argc, char **argv)
{
    if (argc != 2)
    {
        fputs("Usage: safe <combination>\n", stderr);
        return 1;
    }

    char entered_password[PW_LEN + 1] = {0};
    strncpy(entered_password, argv[1], PW_LEN);

    char* fname = "combination.txt";
    if(access(fname , F_OK ) == -1)
    {
        fname = "01_safe/combination.txt";
    }

    FILE *pw_file = fopen(fname, "rb");
    if (!pw_file)
    {
        fputs("Error opening combination file\n", stderr);
        return 1;
    }

    char password[PW_LEN + 2] = {0};
    char *res = fgets(password, sizeof(password), pw_file);
    if (!res)
    {
        fputs("Error reading combination\n", stderr);
        return 1;
    }

    // remove trailing newline if any
    size_t len = strlen(entered_password);
    if (len > 0 && entered_password[len - 1] == '\n')
    {
        entered_password[len - 1] = '\0';
    }

    // constant time comparison
    puts("Trying to open the safe...");
    int diff = constant_time_strcmp(password, entered_password, PW_LEN);

    if (diff != 0)
    {
        puts("The safe seems to resist your attempt");
        return 1;
    }

    puts("The safe springs open. Inside you see:");

    fname = "secret.txt";
    if(access(fname , F_OK ) == -1)
    {
        fname = "01_safe/secret.txt";
    }

    FILE *secret = fopen(fname, "rb");
    if (!secret)
    {
        fputs("Error opening secret file\n", stderr);
        return 1;
    }

    char secret_buf[128] = {0};
    if (!fgets(secret_buf, sizeof(secret_buf), secret))
    {
        fputs("Error reading secret\n", stderr);
        fclose(secret);
        return 1;
    }

    fclose(secret);
    puts(secret_buf);

    return 0;
}

FAULT_CONFIG("TIMEOUT=30");
FAULT_CONFIG("NOASLR");
FAULT_CONFIG("NOHAVOC");
FAULT_CONFIG("NOZERO");
FAULT_CONFIG("NOBITFLIP");
FAULT_CONFIG("NOEXITMSG");
FAULT_CONFIG("MAXFAULTS=1");
FAULT_CONFIG_A("MAIN", main);
