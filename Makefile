.PHONY: run init migrate upgrade downgrade show

run:
	gunicorn hexlistserver:app

init:
	python hexlistserver/manage.py db init

migrate:
	python hexlistserver/manage.py db migrate

upgrade:
	python hexlistserver/manage.py db upgrade

downgrade:
	python hexlistserver/manage.py db downgrade

show:
	python hexlistserver/manage.py db show