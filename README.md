```
 _               _ _     _
| |__   _____  _| (_)___| |_ ___  ___ _ ____   _____ _ __ 
| '_ \ / _ \ \/ / | / __| __/ __|/ _ \ '__\ \ / / _ \ '__|
| | | |  __/>  <| | \__ \ |_\__ \  __/ |   \ V /  __/ |
|_| |_|\___/_/\_\_|_|___/\__|___/\___|_|    \_/ \___|_|   
                                                        
```

hexlist is an API for storing and retrieving links

#setup

python flask app

postgresdb with flask-sqlalchemy

heroku hosting and heroku postgres db

#development

1 - run unit tests
2 - tests locally by running 'make run' then [test the feature with postma](https://www.getpostman.com/).
3 - then upload to staging heroku and tests feature
4 - then once you're sure it works upload to prodduction heroku

`Procfile`:

used by heroku, tells eroku what process to run

`runtime.txt`:

overrides the default config on heroku setup to run python 3 instaed of default python 2.

`requirements.txt`:

file with dependencies for heroku or pip to install

`manage.py`:

a file that we run via make file to manage database migrations

run `make init` - initilaize db (shouldn't need to do)

run `make migrate` - make a migration with the current data models/tables defined in those models.

run `make upgrade` - upgrade your db with the new migration.

`env.sh`:

a file that contains development environment variables

run `source env.sh` to setup local env variables properly

`config.py`:

a file that contains our configuration info

set a subsection of the config file to be your app's config by running

`export APP_SETTINGS="hexlistserver.config.DevelopmentConfig"` (or see env.sh)

or to set it permanently on heroku app, switch stage for prod

`heroku config:set APP_SETTINGS=hexlistserver.config.StagingConfig --remote stage`

#api

`GET /hex/get/<int:hex_object_id>`

`POST /hex/post/`

`DELETE /hex/delete/<int:hex_object_id>`

#store

#retrieve

#resources

[flask quickstart](http://flask.pocoo.org/docs/0.10/quickstart/)

start with this tutorial (ignore autoenv):
[heroku flask postgres workflow](https://realpython.com/blog/python/flask-by-example-part-1-project-setup/)

[deploying-a-flask-application-to-heroku](https://community.nitrous.io/tutorials/deploying-a-flask-application-to-heroku)

[discover flask - great resource](https://github.com/realpython/discover-flask)

[great tutorial on alembic and db migration](http://blog.miguelgrinberg.com/post/flask-migrate-alembic-database-migration-wrapper-for-flask)

[good video on alembic and migrations](https://www.youtube.com/watch?v=YJibNSI-iaE )

[flask-by-example-part-2-postgres-sqlalchemy](https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/)

[flask mega tutorial] (http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xviii-deployment-on-the-heroku-cloud)

[how to - flask migrate](https://www.youtube.com/watch?v=YJibNSI-iaE )

[heroku Procfile](https://devcenter.heroku.com/articles/procfile)

[heroku config vars](https://devcenter.heroku.com/articles/config-vars)

[psql shell guide](http://postgresguide.com/utilities/psql.html)

[psycopg docs](http://initd.org/psycopg/docs/)

[http verbs](http://www.restapitutorial.com/lessons/httpmethods.html)

#author

[yvan](https://github.com/yvan)
