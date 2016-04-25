```
 _               _ _     _
| |__   _____  _| (_)___| |_ ___  ___ _ ____   _____ _ __ 
| '_ \ / _ \ \/ / | / __| __/ __|/ _ \ '__\ \ / / _ \ '__|
| | | |  __/>  <| | \__ \ |_\__ \  __/ |   \ V /  __/ |
|_| |_|\___/_/\_\_|_|___/\__|___/\___|_|    \_/ \___|_|   
                                                        
```

hexlist is an API for storing and retrieving links

#/api/v1.0/token

GET:

`curl -u dev:dev -X GET http://localhost:8000/api/v1.0/token`

#/api/v1.0/user

POST:

`curl -u user:password -i -X POST -H "Content-Type: application/json" -d '{"username":"dev","password":"dev"}' http://127.0.0.1:8000/api/v1.0/user`

GET:

`curl -u dev:dev -i -X GET http://127.0.0.1:8000/api/v1.0/user/7851171`

DELETE:

`curl -u dev:dev -X DELETE http://localhost127.0.0.1:8000/api/v1.0/user/7851171`

#store

#retrieve

#using curl

-u username:password is a way ot authenticate to the API. altough you should use a token instead.

creating a user already requires the existence of a user, to get around this. on a live DB just copy a local DB entry and manually insert it into heroku postgres, once that's done you can use that user to generate tokens make yous password a long unhackable phrase (at least 4-5 words, some numbers, and special chars)

type `curl -h` to see what these options mean

#development

1 - run unit tests

2 - tests locally by running 'make run' then [test the feature with postman](https://www.getpostman.com/).

3 - then upload to staging heroku and tests feature

4 - then once you're sure it works upload to prodduction heroku 'git push https://git.heroku.com/hexlistserver-prod.git master', i dont add a second remote because 1, we should be careful bout what we push to prod, 2, heroku is a lot less verbose when there's one remote.

`start postgres locally`:

`pg_ctl start -D /usr/local/var/postgres/`

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

or to set it permanently on heroku staging app:

`heroku config:set APP_SETTINGS=hexlistserver.config.StagingConfig`

or production:

`heroku config:set APP_settings=hexlistserver.config.ProductionConfig --remote https://git.heroku.com/hexlistserver-prod.git`

env variables should look like:

```
APP_SETTINGS: hexlistserver.config.ProductionConfig
DATABASE_URL: postgres://postgresuser:password@ec2ipaddr.compute-1.amazonaws.com:PORT/DBNAME
```

#setup

python flask app

postgresdb with flask-sqlalchemy

heroku hosting and heroku postgres db


#resources

[flask quickstart](http://flask.pocoo.org/docs/0.10/quickstart/)

[good tut on basic rest API, read first](http://blog.miguelgrinberg.com/post/restful-authentication-with-flask)

[follow up on the last one that lets you generate tokens](http://blog.miguelgrinberg.com/post/restful-authentication-with-flask)

this tutorial (ignore autoenv):
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
