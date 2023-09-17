SRCS = $(wildcard *.c)
OBJS = $(patsubst %.c,%.o,$(SRCS))

all: $(OBJS) eddsa.a

%.o: %.c
	$(CC) -g -O3 -o $@ -c $<
	
eddsa.a: $(OBJS)
	ar -rcs eddsa.a $(OBJS)
	
clean:
	rm -rf ($OBJS) eddsa.a

