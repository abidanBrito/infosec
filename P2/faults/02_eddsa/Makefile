ECCPROG = eddsa
ECCKG = eddsakg
ECCOBJS = ref10/eddsa.a

all: $(ECCPROG) $(ECCKG)

ref10/eddsa.a:
	 $(MAKE) -C ref10

eddsa: eddsa.c $(ECCOBJS)
	$(CC) $(CFLAGS) -g -I../ -static -o $@  $< $(ECCOBJS)

eddsakg: eddsakg.c $(ECCOBJS)
	$(CC) $(CFLAGS) -I../ -static -o $@ $< $(ECCOBJS)
	
clean:
	rm -f simulator $(ECCPROG) $(ECCKG) $(ECCOBJS)
