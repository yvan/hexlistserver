.PHONY: run

run:
	gunicorn hexlistserver:app
	