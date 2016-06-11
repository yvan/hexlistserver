```
 _               _ _     _
| |__   _____  _| (_)___| |_ ___  ___ _ ____   _____ _ __ 
| '_ \ / _ \ \/ / | / __| __/ __|/ _ \ '__\ \ / / _ \ '__|
| | | |  __/>  <| | \__ \ |_\__ \  __/ |   \ V /  __/ |
|_| |_|\___/_/\_\_|_|___/\__|___/\___|_|    \_/ \___|_|   
                                                        
```

hexlist is an API for storing and retrieving links

the staging server is at:

`https://hexlistserver-stage.herokuapp.com/`

ther production server is at:

`https://hexlistserver-prod.herokuapp.com/`

#/api/v1.0/token

GET:

`curl -u dev:dev -X GET http://localhost:8000/api/v1.0/token`

#/api/v1.0/user

POST:

`curl -u user:password -i -X POST -H "Content-Type: application/json" -d '{"username":"dev","password":"dev"}' http://127.0.0.1:8000/api/v1.0/user`

GET:

`curl -u dev:dev -i -X GET http://127.0.0.1:8000/api/v1.0/user/7851171`

DELETE:

`curl -u dev:dev -X DELETE http://127.0.0.1:8000/api/v1.0/user/7851171`

#/api/v1.0/hex

GET:

`curl -u dev:dev -i -X GET http://127.0.0.1:8000/api/v1.0/hex/6418073`

POST:

`curl -u dev:dev -i -X POST http://localhost:8000/api/v1.0/hex -H "Content-Type: application/json" -d '{"name": "yvan_hex_1", "owner_id":434596, "image_path":"http://yvanscher.com/favicon.ico", "user_id":434596}'`

DELETE:

`curl -i -X DELETE http://localhost:8000/api/v1.0/hex/5605321 -u dev:dev`

#/api/v1.0/link

GET:

`curl -u dev:dev -i -X GET http://127.0.0.1:8000/api/v1.0/link/7059414`

POST:

`curl -u dev:dev -i -X POST -H "Content-Type: application/json" -d '{"url":"yvanscher.com", "description":"a link to yvan\'s personal site", "hex_object_id":7248714}' http://127.0.0.1:8000/api/v1.0/link`

DELETE:

`curl -u dev:dev -i -X DELETE http://127.0.0.1:8000/api/v1.0/link/7059414`

#/api/v1.0/location

GET:

`curl -u dev:dev -i -X GET http://localhost:8000/api/v1.0/location/534f6e75-93a6-4b6d-9dcf-85ae20fcb144`

POST:

`curl -u dev:dev -i -X POST  http://localhost:8000/api/v1.0/location -H "Content-Type: application/json" -d '{"platform":"ios","location":"myhexlist", "hex_object_id":"534f6e75-93a6-4b6d-9dcf-85ae20fcb144"}'`

DELETE:

`curl -u dev:dev -i -X DELETE http://localhost:8000/api/v1.0/location/534f6e75-93a6-4b6d-9dcf-85ae20fcb144`

#/api/v1.0/send

GET:

`curl -u dev:dev -i -X GET http://localhost:8000/api/v1.0/send/175823b5-64a1-47d0-a6a6-81f2c685af11`

POST:

`curl -u dev:dev -i -X POST  http://localhost:8000/api/v1.0/send -H "Content-Type: application/json" -d '{"sender_id":"d7c2f463-736f-467e-a317-a6e4b64cd6a6","recipient_id":"9066e9a9-bc47-4f12-8436-551695026421", "hex_object_id":"175823b5-64a1-47d0-a6a6-81f2c685af11"}'`

DELETE:

`curl -u dev:dev -i -X DELETE http://localhost:8000/api/v1.0/send/175823b5-64a1-47d0-a6a6-81f2c685af11`

#using curl

-u username:password is a way ot authenticate to the API. altough you should use a token instead. to use a token, first hit the token generation api [endpoint](#/api/v1.0/token), get a token and use it instead of the username (password can be any word w/ a token) like:

`curl -u eyJpYXQiOjE0NjM5NDkyMzksImV4cCI6MTQ2NDAzNTYzOSwiYWxnIjoiSFMyNTYifQ.eyJpZCI6NTI3NDA3OX0.Tc_0outiJw1xIXFWO1HTyYhFXR9oh4h1eLVoYPHEke:whatever`

creating a user already requires the existence of a user, to get around this. on a live DB just copy a local DB entry and manually insert it into heroku postgres, once that's done you can use that user to generate tokens make yous password a long unhackable phrase (at least 4-5 words, some numbers, and special chars). you can manually insert this user onto the staging server like so: .

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

the same applies to these environment vars for email error reporting:
```
MAIL_SERVER='smtp.gmail.com'
MAIL_PORT=465
MAIL_USERNAME='hexlist.worker.bees@gmail.com'
MAIL_PASSWORD='DA_PASSWURD'
```
these env variables are only set on the production server, because on staging DEBUG=True, the error handler never fires on the staging server. they were originally tested locally by setting the local development config to have DEUG=False temporarily.

env variables should look like:

```
APP_SETTINGS: hexlistserver.config.ProductionConfig
DATABASE_URL: postgres://postgresuser:password@ec2ipaddr.compute-1.amazonaws.com:PORT/DBNAME
```

migrating the db on herkou:

```
git push stage master
heroku run make migrate # if you didnt migrate locally you need this line, creates the migration
heroku run make upgrade # either way you need this line, actually moves the db to this migration
```

dev user pass - dev:dev
yvan user pass - yvan:getmysquanchon

upgrading to the next level of db on heroku:
[https://devcenter.heroku.com/articles/upgrading-heroku-postgres-databases](https://devcenter.heroku.com/articles/upgrading-heroku-postgres-databases)

adding namecheap ssl certificate:
[https://www.resumonk.com/blog/setup-ssl-certificate-heroku/](https://www.resumonk.com/blog/setup-ssl-certificate-heroku/)

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

[error handling and reporting implementation](http://flask.pocoo.org/docs/0.11/errorhandling/)

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
