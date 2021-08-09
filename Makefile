# define the name of the virtual environment directory
VENV := venv
COMPOSE = docker-compose

.PHONY: all venv run clean virtualenv startup drop

# default target, when make executed without arguments
all: venv

$(VENV)/bin/activate: virtualenv requirements.txt
	echo "Creating virtualenv and installing requirements"
	python3 -m virtualenv $(VENV)
	./$(VENV)/bin/pip install -r requirements.txt

virtualenv:
	echo "Ensuring virtualenv exists"
	which virtualenv

# venv is a shortcut target
venv: $(VENV)/bin/activate

run:
	echo "Running development server"
	./$(VENV)/bin/python3 manage.py migrate
	./$(VENV)/bin/python3 manage.py runserver

startup: venv drop
	echo "Starting up DB and creating a super user"
	docker-compose up -d
	sleep 5
	./$(VENV)/bin/python3 manage.py migrate
	./$(VENV)/bin/python3 manage.py createsuperuser
	./$(VENV)/bin/python3 manage.py collectstatic

drop:
	docker-compose down -v

reset-virtualenv:
	python3 -m virtualenv --clear $(VENV)

clean-cached-python:
	find . -type f -name '*.pyc' -delete
