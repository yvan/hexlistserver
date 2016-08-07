.PHONY: run init migrate upgrade downgrade show stage

run:
	gunicorn hexlistserver.app:app --reload

stage:
	git push stage master

prod:
	git push prod master

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

revision:
	python manage.py db revision
