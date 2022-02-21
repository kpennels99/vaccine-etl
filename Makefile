# define the name of the virtual environment directory
VENV := venv
COMPOSE = docker-compose

.PHONY: all django_run venv django_run clean virtualenv drop

all: startup ## default target, activate

help: ## print help messages
	@sed -n 's/^\([a-zA-Z_-]*\):.*## \(.*\)$$/\1 -- \2/p' Makefile


$(VENV)/bin/activate: virtualenv 
	echo "Creating virtualenv and installing requirements"
	python3 -m venv $(VENV)
	

virtualenv: ## Check if virtual environment exists
	echo "Ensuring python3 exists"
	which python3

activate_install: src/django/requirements.txt ## activate virtual environment and install packages.
	(source $(VENV)/bin/activate; $(VENV)/bin/pip install -r src/django/requirements.txt;)

venv: $(VENV)/bin/activate activate_install## Activate virtual environment

start: venv
	docker-compose up -d

postgres_start: 
	docker-compose up -d postgresql

celery_start: 
	docker-compose up -d celery-worker

airflow_start: ## create services necessary to run django
	docker-compose up -d airflow-scheduler airflow-worker airflow 

django_start: ## create services necessary to run django
	docker-compose up -d django-webserver celery-worker
	
django_create: venv django_start ## create new installation of django
	./$(VENV)/bin/python3 src/django/manage.py migrate
	./$(VENV)/bin/python3 src/django/manage.py createsuperuser
	./$(VENV)/bin/python3 src/django/manage.py collectstatic

django_run_locally: celery_start venv ## Start django development server
	echo "Running development server"
	./$(VENV)/bin/python3 src/django/manage.py migrate
	./$(VENV)/bin/python3 src/django/manage.py runserver

logs: ## View container logs 
	docker-compose logs -f --tail=20

stop: ## Stop all runniing containers
	docker-compose down
	
drop: ## Delete associate volumes when stopping containers
	docker-compose down -v

reset-virtualenv: ## Delete all installed pip packages
	rm -rf ./$(VENV)

clean-cached-python: ## Delete all *.pyc files
	find . -type f -name '*.pyc' -delete