VICTIMSRCS = $(wildcard demos/victim*.c)
VICTIMPROGS = $(patsubst %.c,%,$(VICTIMSRCS))
CFLAGS = -Wno-unused-result

all: simulator $(VICTIMPROGS)

simulator: simulator.c
	gcc $(CFLAGS) simulator.c -o simulator -Os
	gcc $(CFLAGS) simulator.c -o 01_safe/simulator -Os -DFBINARY=safe -DFSCRIPT=safe.fault
	gcc $(CFLAGS) simulator.c -o 02_eddsa/simulator -Os -DFBINARY=eddsa -DFSCRIPT=eddsa.fault
	gcc $(CFLAGS) simulator.c -o 03_aes/simulator -Os -DFBINARY=aes -DFSCRIPT=aes.fault

%: %.c
	$(CC) $(CFLAGS) -I./ -static -o $@ $<

clean:
	rm -f simulator $(VICTIMPROGS)
