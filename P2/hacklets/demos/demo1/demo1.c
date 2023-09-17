#include <err.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>

// Function printing the secret flag
void print_flag()
{
  char* flag = NULL;
  size_t n = 0;

  FILE* flagfile = fopen("flag.txt", "r");
  if (flagfile == NULL)
  {
    err(-1, "Sorry couldn't open flag :( report this to the admin!");
  }

  getline(&flag, &n, flagfile);
  printf("There you go:\n%s\n", flag);

  free(flag);
}

void vuln(void)
{
  volatile int modified;
  char buffer[64];

  modified = 0;
  fgets(buffer, 0x64, stdin);

  if (modified != 0)
  {
    print_flag();  // CAN WE GET HERE?
    exit(0);
  }
  else
  {
    puts("Nope! Needs a little more juice!");
    exit(1);
  }
}

int main(int argc, char** argv)
{
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
  vuln();
  return 0;
}
