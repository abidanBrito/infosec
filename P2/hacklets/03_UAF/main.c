#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <math.h>
#include <sys/random.h>

#define CREATE_CARD 1
#define OPEN_RED_DOOR 2
#define DELETE_CARD 3
#define EXIT 4

#define GREEN_CARD_OPTION 1
#define YELLOW_CARD_OPTION 2
#define RED_CARD_OPTION 3

#define GREEN_CARD_ID 123.456f
#define YELLOW_CARD_ID 0.815f
#define RED_CARD_ID 25.8069758011f

// Green access card with 28 byte password
struct GreenAccessCard
{
  char pin[28];
  float cardID;
} typedef GreenAccessCard;

// Yellow access card with 32 byte password
struct YellowAccessCard
{
  char pin[32];
  float cardID;
} typedef YellowAccessCard;

// Red access card with 36 byte password
struct RedAccessCard
{
  char pin[36];
  float cardID;
} typedef RedAccessCard;

char *redCardMasterPwd;

GreenAccessCard *green_access_card = NULL;
YellowAccessCard *yellow_access_card = NULL;
RedAccessCard *red_access_card = NULL;

//-----------------------------------------------------------------------------
// Helper functions
//-----------------------------------------------------------------------------

int read_integer()
{
  int temp = 0;
  scanf("%d", &temp);
  while (getchar() != '\n');
  return temp;
}

void printIntro()
{
  puts("==========================================================================================================");
  puts("  LOCKED DOOR GAME");
  puts("==========================================================================================================");
  puts("> Your goal is to get access to the red door.");
  puts("> But it is locked and requires a red access card and the password to open it.");
  puts("> At the beginning, you are given one red card, but no one told you the secret admin password...");
  puts("----------------------------------------------------------------------------------------------------------");
  puts("> You can create green and yellow access cards and set a user defined password.");
  puts("> The red access card uses a master password that is the same for all red cards.");
  puts("> You can only have one card of each type.");
  puts("----------------------------------------------------------------------------------------------------------");
  puts("> Hint: You can also destroy cards you created. Maybe you could gain some advantage that way?");
  puts("> Good luck to you!");
  puts("==========================================================================================================");
}

void printOptions()
{
  puts("\nWhat can I do for you?");
  puts("[1] Create Card");
  puts("[2] Open Red Door");
  puts("[3] Delete Card");
  puts("[4] Exit");
  fputs("> ", stdout);
}

void checkIfCardPtrIsNull(void *ptr)
{
  if (ptr == NULL)
  {
    puts("Card does not exist.");
    exit(1);
  }
}

float getIdOfCard(int card_choice)
{
  switch (card_choice)
  {
    case 1:
    {
      checkIfCardPtrIsNull(green_access_card);
      return green_access_card->cardID;
    }
    case 2:
    {
      checkIfCardPtrIsNull(yellow_access_card);
      return yellow_access_card->cardID;
    }
    case 3:
    {
      checkIfCardPtrIsNull(red_access_card);
      return red_access_card->cardID;
    }
  }
  puts("Invalid choice.");
  exit(1);
}

int getCardChoiceFromUser()
{
  printf("[%d] Green\n", GREEN_CARD_OPTION);
  printf("[%d] Yellow\n", YELLOW_CARD_OPTION);
  printf("[%d] Red\n", RED_CARD_OPTION);
  return read_integer();
}

//-----------------------------------------------------------------------------
// Important functions
//-----------------------------------------------------------------------------

int isCardValid(char *correct_card_pwd, float correct_card_id, char *user_input_pwd, float chosen_card_id)
{
  if (strncmp(correct_card_pwd, user_input_pwd, 36) == 0)
  {
    if (fabs(correct_card_id - chosen_card_id) < 0.001)
    {
      return 1;
    }
    puts("Wrong card ID for chosen door.");
    return 0;
  }
  puts("Wrong password for chosen card.");
  return 0;
}

GreenAccessCard *createGreenCard()
{
  // I hope I did not make any mistakes in this function
  puts("Creating green access card...");
  GreenAccessCard *card = malloc(sizeof(GreenAccessCard));
  fputs("Choose Password: ", stdout);
  scanf("%28s", card->pin);
  card->cardID += GREEN_CARD_ID;
  puts("Created green access card.");
  return card;
}

YellowAccessCard *createYellowCard()
{
  // I hope I did not make any mistakes in this function
  puts("Creating yellow access card...");
  YellowAccessCard *card = malloc(sizeof(YellowAccessCard));
  fputs("Choose Password: ", stdout);
  scanf("%32s", card->pin);
  card->cardID += YELLOW_CARD_ID;
  puts("Created yellow access card.");
  return card;
}

void freeCard(void *card)
{
  checkIfCardPtrIsNull(card);
  free(card);
}

int main()
{
  // Create red access card with super secret red card admin pwd
  red_access_card = malloc(sizeof(RedAccessCard));
  red_access_card->cardID = RED_CARD_ID;
  unsigned int seed;
  getrandom(&seed,sizeof (unsigned int),0);
  srand(seed);
  for (int i = 0; i < 36; i++)
  {
    red_access_card->pin[i] = (char) rand();
  }
  red_access_card->pin[35] = 0;

  // It is going to be the same for all red cards so better store it somewhere
  redCardMasterPwd = red_access_card->pin;

  printIntro();

  int decision = 0;
  while (decision != EXIT)
  {
    printOptions();
    decision = read_integer();
    switch (decision)
    {
      case CREATE_CARD:
      {
        puts("Which access card do you want to create?");
        int card_choice = getCardChoiceFromUser();

        if (card_choice == GREEN_CARD_OPTION)
        {
          if (green_access_card != NULL)
          {
            puts("You already have a green access card.");
            puts("Delete this card first before you create a new one.");
            continue;
          }
          green_access_card = createGreenCard();
        }
        else if (card_choice == YELLOW_CARD_OPTION)
        {
          if (yellow_access_card != NULL)
          {
            puts("You already have a yellow access card");
            puts("Delete this card first before you create a new one.");
            continue;
          }
          yellow_access_card = createYellowCard();
        }
        else if (card_choice == RED_CARD_OPTION)
        {
            puts("Nope...");
        }
        else
        {
          puts("Invalid choice.");
        }
        continue;
      }
      case OPEN_RED_DOOR:
      {
        puts("Which card do you want to use to open the red door?");
        int card_choice = getCardChoiceFromUser();
        float chosen_card_id = getIdOfCard(card_choice);

        puts("To enter the red door, please enter the red card master password:");
        char user_input_pwd[36] = {0};
        fgets(user_input_pwd, 36, stdin);

        // Password and ID need to be of red access card to open the red door.
        if (isCardValid(redCardMasterPwd, RED_CARD_ID, user_input_pwd, chosen_card_id))
        {
          puts("You successfully opened the secret red door and found the flag.");
          execl("/bin/cat", "cat", "flag.txt", NULL);
          exit(0);
        }
        continue;
      }
      case DELETE_CARD:
      {
        puts("Which access card do you want to delete?");
        int card_choice = getCardChoiceFromUser();

        if (card_choice == GREEN_CARD_OPTION)
        {
          freeCard(green_access_card);
          green_access_card = NULL;
        }
        else if (card_choice == YELLOW_CARD_OPTION)
        {
          freeCard(yellow_access_card);
          yellow_access_card = NULL;
        }
        else if (card_choice == RED_CARD_OPTION)
        {
          freeCard(red_access_card);
          red_access_card = NULL;
        }
        else
        {
          puts("Invalid choice.");
        }
        continue;
      }
      case EXIT:
      {
        puts("Bye, have a nice day.");
        exit(0);
      }
    }
  }
  return 0;
}
