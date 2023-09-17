PYTHON=python3

CHALLENGES=API1 XSS1 SQLi1 SQLi2 XSS2 SQLi3 File1 File2 SSTI API2 JWT

all:
	make build

reset-all:
	docker system prune -a -f
	docker volume rm $(shell docker volume ls -qf dangling=true)

reset:
	(for F in $(CHALLENGES); do cd $$F; make remove; cd ..; done)

build:
	(for F in $(CHALLENGES); do cd $$F; make build; cd ..; done)

clean: reset rm_pycache


rm_pycache:
	(for F in $(CHALLENGES); do cd $$F/attack_script; rm -rf __pycache__; rm -rf *.pyc; cd ../..; done)

.PHONY: all reset clean build reset-all rm_pycache 
