#!/bin/bash

ifndef TARGET
override TARGET = django-app
endif

ifndef UID
override UID = 1001
endif

DOCKER_COMPOSE = docker-compose --project-name boatsandjoy

# General commands

# General commands

build:
	$(DOCKER_COMPOSE) build

up:
	$(DOCKER_COMPOSE) up -d

down:
	$(DOCKER_COMPOSE) down

restart:
	$(DOCKER_COMPOSE) restart

kill:
	$(DOCKER_COMPOSE) kill

stop:
	$(DOCKER_COMPOSE) stop

ps:
	$(DOCKER_COMPOSE) ps

rm:
	$(DOCKER_COMPOSE) rm

ssh:
	$(DOCKER_COMPOSE) run --entrypoint bash ${TARGET}

log:
	$(DOCKER_COMPOSE) logs -f --tail 100 ${TARGET}

clean:
	$(DOCKER_COMPOSE) down -v --rmi all --remove-orphans

# Django commands

shell:
	$(DOCKER_COMPOSE) run --user=${UID} --rm --entrypoint python django-app manage.py shell_plus

showmigrations:
	$(DOCKER_COMPOSE) run --user=${UID} --rm --entrypoint python django-app manage.py showmigrations $(args)

makemigrations:
	$(DOCKER_COMPOSE) run --user=${UID} --rm --entrypoint python django-app manage.py makemigrations $(args)

migrate:
	$(DOCKER_COMPOSE) run --user=${UID} --rm --entrypoint python django-app manage.py migrate $(args)

collectstatic:
	$(DOCKER_COMPOSE) run --user=${UID} --rm --entrypoint python django-app manage.py collectstatic --noinput

createsuperuser:
	$(DOCKER_COMPOSE) run --user=${UID} --rm --entrypoint python django-app manage.py createsuperuser

dbshell:
	$(DOCKER_COMPOSE) run --user=${UID} --rm --entrypoint python django-app manage.py dbshell

makemessages:
	$(DOCKER_COMPOSE) run --user=${UID} --rm --entrypoint python django-app manage.py makemessages --all

compilemessages:
	$(DOCKER_COMPOSE) run --user=${UID} --rm --entrypoint python django-app manage.py compilemessages
