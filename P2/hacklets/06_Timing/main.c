#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define array_size 9

char user_input[array_size];
char pwd[array_size];


int checkPassword()
{
    for (int i = 0; i < array_size; i++)
    {
        if (user_input[i] != pwd[i])
        {
            return 0;
        }
        // Due to the high energy prices we need to let the program rest a bit
        usleep(2000);
    }
    return 1;
}

void readStaticPassword()
{
    FILE *fp;
    fp = fopen("password.txt", "r");
    if (fp == NULL)
    {
        puts("Password file not found");
        exit(-1);
    }
    if (fgets(pwd, array_size, fp) == NULL)
    {
        puts("Error reading password file");
        exit(-1);
    }
    fclose(fp);
}

int main()
{
    // Reading in a 12 char password made up of lower-
    // and uppercase letters, numbers and special characters
    readStaticPassword();
    puts("What is the secret password?");
    while (1)
    {
        fputs("> ", stdout);
        fflush(stdout);
        // Reading in the user input
        fgets(user_input, array_size, stdin);

        if (checkPassword() == 1)
        {
          puts("Provided password was correct");
          puts("The flag is: ");
          execl("/bin/cat", "cat", "flag.txt", NULL);
          fflush(stdout);
          break;
        }
        else
        {
          puts("Provided password was incorrect try again");
          fflush(stdout);
        }
    }
    return 0;
}
