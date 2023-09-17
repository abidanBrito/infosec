#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include <sys/types.h>
#include <time.h>
#include <unistd.h>

#define BUFFER_SIZE 16
#define USER_INPUT 64

int patience = 5;

void readFlag(char *target_buffer, int size)
{
  FILE *file;
  int i = 0;
  file = fopen("flag.txt", "r");
  if (file)
  {
    while (i < size && target_buffer[i] != EOF)
    {
      target_buffer[i] = (char) fgetc(file);
      i++;
    }
  }
  fclose(file);
}

void readStringInput(char *target_buffer, int size)
{
  int c;
  int i = 0;
  while ((c = getchar()) != '\n' && c != EOF)
  {
    if (i < size)
    {
      target_buffer[i] = (char) c;
      i++;
    }
  }
}

void printWelcomeMessage()
{
  printf("[Chat bot]: Hi I am a 'helpful' chat bot.\n");
  printf("[Chat bot]: Tell me how you tried to solved this challenge.\n");
  printf("[Chat bot]: If I am impressed by your approach, I might show you the flag.\n");
  printf("[Chat bot]: But first, what is your name?\n");
}

int main()
{
  char flag[64] = {0};
  char username[BUFFER_SIZE] = {0};
  printWelcomeMessage();
  // What is this pointer even doing here?
  void *useless_username_ptr = &username;
  readStringInput(username, BUFFER_SIZE);

  int impressed = 0;
  printf("[Chat bot]: So what, did you try to solve this challenge?\n");
  while (patience)
  {
    char userinput[USER_INPUT] = {0};
    printf("[%s]: ", username);
    readStringInput(userinput, USER_INPUT - 1);
    printf("[Chat bot]: Okay, you tried: ");
    printf(userinput);
    fflush(stdout);
    printf("\n");
    impressed += 1;
    patience--;
  }
  if (impressed > 20)
  {
    readFlag(flag, 64);
    printf("That was impressive! But you still dont get my flag, ");
    printf(username);
    fflush(stdout);
  }
  else
  {
    printf("Sorry, but I am not impressed. Bye!\n");
  }
  return 0;
}
