#include <stdio.h>
#include <stdlib.h>
#include <string.h>

//Why is this even here?!
void openFlag()
{
    FILE* file;
    char c = 0;
    file = fopen("flag.txt","r");
    if(file)
    {
        c = fgetc(file);
        while(c != EOF)
        {
            printf("%c",c);
            c = fgetc(file);
        }
        printf("\n");
        fflush(stdout);
    }
    fclose(file);
}

void printWelcomeMessage()
{
    puts("   ____                    ____                       __             _    ");
    puts("  / __/_ _____  ___ ____  / __/__ ______ _________   / /  ___  ___ _(_)__ ");
    puts(" _\\ \\/ // / _ \\/ -_) __/ _\\ \\/ -_) __/ // / __/ -_) / /__/ _ \\/ _ `/ / _ \\");
    puts("/___/\\_,_/ .__/\\__/_/   /___/\\__/\\__/\\_,_/_/  \\__/ /____/\\___/\\_, /_/_//_/");
    puts("        /_/                                                  /___/        ");
}

void readInput(char *target_buffer, int size)
{
    int c;
    int i = 0;
    while ((c = getchar()) != '\n' && c != EOF)
    {
        if(i < size)
        {
            target_buffer[i] = (char)c;
            i++;
        }
    }
    target_buffer[size-1] = '\0';
}

int main()
{
    char username[016];
    char password[016];
    int username_len = 16;
    int password_len = 16;
    printWelcomeMessage();

    puts("Username:");
    readInput(username, username_len);

    puts("Password:");
    readInput(password, password_len);

    if(strncmp(username, "admin", 5) == 0)
    {
        // Oof I nearly called the openFlag function without checking the password
        // openFlag();
        puts("Still under construction");
        return 0;
    } else {
        puts("Bye, have a great time");
        exit(0);
    }
    return 0;
}
