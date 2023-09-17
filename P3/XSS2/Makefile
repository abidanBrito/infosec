all:
	docker-compose build && docker-compose up

run:
	docker-compose up

build:
	docker-compose build

remove:
	docker-compose down

attack:
	python3 ./attack_script/attack.py

victim:
	python3 ./attack_script/victim.py www/admin.pw

.PHONY: all run build remove attack admin
