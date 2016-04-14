.PHONY: run init migrate upgrade downgrade show

run:
	gunicorn hexlistserver:app

init:
	python manage.py db init

migrate:
	python manage.py db migrate

upgrade:
	python manage.py db upgrade

downgrade:
	python manage.py db downgrade

show:
	python manage.py db show