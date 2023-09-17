#include <err.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>

void read_flag(char *buffer)
{
  size_t n = 0;

  FILE *flagfile = fopen("flag.txt", "r");
  if (flagfile == NULL){
    err(-1, "Sorry couldn't open flag :( report this to the admin!");
  }

  fscanf(flagfile, "%s", buffer);
  fclose(flagfile);
}

typedef struct User{
  char username[20];
  char user_secret[50];
} User;

void printOptions(){
  puts("\n1. Read user_secret");
  puts("2. Delete user");
  puts("3. Exit");
  puts("Choose option");
  printf("> ");
}

int getUserId(){
  puts("What user do you want to access?");
  printf("> ");
  int user;
  scanf("%d", &user);
  if (user < 0 || user > 2){
    exit(0);
  }
  return user;
}

void vuln(){
  User *user[2];
  int access[2];

  user[0] = malloc(sizeof(User));
  strncpy(user[1]->username, "admin", 6);
  read_flag(user[0]->user_secret);
  access[0] = 0;

  user[1] = malloc(sizeof(User));
  strncpy(user[1]->username, "default user", 12);
  strncpy(user[1]->user_secret, "Boring text", 12);
  access[1] = 1;

  int choice;
  while (1){
    printOptions();
    scanf("%d", &choice);
    switch (choice){
    case 1:{
      int user_id = getUserId();
      if (access[user_id] == 1){
        printf("User secret: %s\n", user[user_id]->user_secret);
      }
      else{
        puts("Access denied");
      }
      break;
    }
    case 2:{
      int user_id = getUserId();
      free(user[user_id]);
      access[user_id] = 1;
      break;
    }
    case 3:{
      puts("Bye");
      exit(0);
      break;
    }
    default:
      puts("Invalid choice");
      exit(1);
      break;
    }
  }

  return;
}

int main()
{
  setvbuf(stdout, NULL, _IONBF, 0);
  setvbuf(stderr, NULL, _IONBF, 0);
  vuln();
  return 0;
}
