all:
	docker-compose build && docker-compose up

run:
	docker-compose up

build:
	docker-compose build

remove:
	docker-compose down -v

attack:
	python3 ./attack_script/attack.py

.PHONY: all run build remove attack
