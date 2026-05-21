DC = docker compose -f docker-compose.dev.yml

up:
	$(DC) up

upd:
	$(DC) up -d

down:
	$(DC) down

build:
	$(DC) build

logs:
	$(DC) logs -f web_dev

shell:
	$(DC) exec web_dev python manage.py shell

migrate:
	$(DC) exec web_dev python manage.py migrate

makemigrations:
	$(DC) exec web_dev python manage.py makemigrations

test:
	$(DC) exec web_dev python manage.py test

messages:
	$(DC) exec web_dev python manage.py makemessages -l es -l en

compilemessages:
	$(DC) exec web_dev python manage.py compilemessages

createsuperuser:
	$(DC) exec web_dev python manage.py createsuperuser

.PHONY: up upd down build logs shell migrate makemigrations test messages compilemessages createsuperuser
