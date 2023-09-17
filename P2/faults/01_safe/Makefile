PWPROG = safe

all: $(PWPROG)

safe: safe.c
	$(CC) $(CFLAGS) -g -I../ -static -o $@ $<

clean:
	rm -f $(PWPROG)
