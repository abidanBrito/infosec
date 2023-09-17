#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <sys/random.h>

unsigned int seed;
char number_of_guesses;
char randomNumbers[128];

// Why is this even here?!
void openFlag(char *filename)
{
  FILE *file;
  char c = 0;
  file = fopen(filename, "r");
  if (file)
  {
    c = fgetc(file);
    while (c != EOF)
    {
      printf("%c", c);
      c = fgetc(file);
    }
    printf("\n");
  }
  fclose(file);
}

void readInput(char *target_buffer, unsigned int size)
{
  int c;
  int i = 0;
  while ((c = getchar()) != '\n' && c != EOF)
  {
    if (i < size)
    {
      target_buffer[i] = (char)c;
      i++;
    }
  }
}

void unsuccessful()
{
  puts("I am sorry your guess was incorrect");
  exit(0);
}

int main()
{
  getrandom(&seed, sizeof (unsigned int), 0);
  srand(seed);
  for (int i = 0; i < 128; i++)
  {
    randomNumbers[i] = rand();
  }

  int (*ptr)() = &main;
  char username[128];
  char *username_ptr = username;
  puts("What is your name?");
  readInput(username_ptr, 128);

  puts("Hello ");
  printf(username);

  puts("How many numbers do you want to guess?");
  int input;
  scanf("%d", &input);
  getchar();
  number_of_guesses = input;

  if (number_of_guesses < 32 || number_of_guesses > 127)
  {
    printf("Your guesses need to be between 32 and 127");
    return 1;
  }
  char predictionInput[number_of_guesses];
  void (*function_ptr)() = &unsuccessful;

  puts("Enter prediction: ");
  readInput(predictionInput, input);

  for (int i = 0; i < number_of_guesses; i++)
  {
    if (predictionInput[i] != randomNumbers[i])
    {
      (*function_ptr)();
      exit(0);
    }
  }
  openFlag("flag.txt");
  fflush(stdout);

  return 0;
}
