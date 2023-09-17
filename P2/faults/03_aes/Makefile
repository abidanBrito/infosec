AESPROG = aes
AESOBJS = tinyAES/aes.o

all: $(AESPROG)

tinyAES/aes.o: 
	 $(MAKE) -C tinyAES

aes: aes.c $(AESOBJS)
	$(CC) $(CFLAGS) -g -I../ -static -o $@ $(AESOBJS) $<

clean:
	rm -f $(AESPROG) $(AESOBJS)
