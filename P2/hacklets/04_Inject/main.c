#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <time.h>
#include <sys/random.h>
#include <sys/stat.h>

int random_nr;
unsigned int seed;

int main()
{
    char buffer[100];
    getrandom(&seed,sizeof (unsigned int),0);

    printf("Hi from %p\n", &buffer);
    puts("Generating random number... ");
    srand(seed);
    random_nr = rand();
    FILE* f = fopen("/tmp/random.txt","w");
    if(f)
    {
      fprintf(f,"%d\n",random_nr);
      fflush(f);
      fchmod(fileno(f), 0640); 
      fclose(f);
    }
    
    printf("%d\n", random_nr);

    puts("Is the random number even or odd?");
    fgets(buffer, 0x100, stdin);

    puts("Thanks for your help. Bye!");
    fflush(stdout);
    return 0;
}