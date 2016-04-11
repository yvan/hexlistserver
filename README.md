```
 _               _ _     _
| |__   _____  _| (_)___| |_ ___  ___ _ ____   _____ _ __ 
| '_ \ / _ \ \/ / | / __| __/ __|/ _ \ '__\ \ / / _ \ '__|
| | | |  __/>  <| | \__ \ |_\__ \  __/ |   \ V /  __/ |
|_| |_|\___/_/\_\_|_|___/\__|___/\___|_|    \_/ \___|_|   
                                                        
```
    export DATABASE_URL="postgresql://localhost/hexlistserver"

hexlist is an API for storing and retrieving links

#setup

python flask app

postgresdb with flask-sqlalchemy

heroku hosting and heroku postgres db

#development

start with this tutorial (ignore autoenv):
[heroku flask postgres workflow](https://realpython.com/blog/python/flask-by-example-part-1-project-setup/)

Procfile:

used by heroku, tells eroku what process to run

runtime.txt:

overrides the default config on heroku setup to run python 3 instaed of default python 2.

requirements.txt:

file with dependencies for heroku or pip to install

manage.py:

a file that we run via make file to manage database migrations

run `make init` - initilaize db (shouldn't need to do)

run `make migrate` - make a migration with the current data models/tables defined in those models.

run `make upgrade` - upgrade your db with the new migration.

env.sh:

a file that contains development environment variables

run `source env.sh` to setup local env variables properly

config.py:

a file that contains our configuration info

set a subsection of the config file to be your app's config by running

`export APP_SETTINGS="config.DevelopmentConfig"` (or see env.sh)

or to set it permanently on heroku app, switch stage for prod

`heroku config:set APP_SETTINGS=config.StagingConfig --remote stage`

#api

#store

#retrieve

#resources

[deploying-a-flask-application-to-heroku](https://community.nitrous.io/tutorials/deploying-a-flask-application-to-heroku)

[flask mega tutorial] (http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xviii-deployment-on-the-heroku-cloud)

[flask-by-example-part-2-postgres-sqlalchemy](https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/)

[heroku Procfile](https://devcenter.heroku.com/articles/procfile)

[heroku config vars](https://devcenter.heroku.com/articles/config-vars)

[psql shell guide](http://postgresguide.com/utilities/psql.html)

[psycopg docs](http://initd.org/psycopg/docs/)

#author

[yvan](https://github.com/yvan)
