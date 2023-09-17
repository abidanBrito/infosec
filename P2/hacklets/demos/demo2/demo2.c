#include <err.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

void read_flag(char *buffer)
{
  size_t n = 0;

  FILE* flagfile = fopen("flag.txt", "r");
  if (flagfile == NULL)
  {
    err(-1, "Sorry couldn't open flag :( report this to the admin!");
  }

   fscanf(flagfile, "%s", buffer);
   fclose(flagfile);
}


void vuln()
{
    char flag[64] = {0};
    char *ptr = flag;
    char username[64] = {0};
    read_flag(flag);    

    puts("Please enter your username");
    printf("> ");
    fgets(username, 64, stdin);

    printf("Hello: ");
    printf(username);
    printf("\n");

    return;
}

int main()
{
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
  vuln();
  return 0;
}
