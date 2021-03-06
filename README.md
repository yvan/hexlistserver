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

# /api/v1.0/token

GET:

`curl -u dev:dev -X GET http://localhost:8000/api/v1.0/token`

# /api/v1.0/user

POST:

`curl -u user:password -i -X POST -H "Content-Type: application/json" -d '{"username":"dev","password":"dev"}' http://127.0.0.1:8000/api/v1.0/user`

GET:

`curl -u dev:dev -i -X GET http://127.0.0.1:8000/api/v1.0/user/7851171`

DELETE:

`curl -u dev:dev -X DELETE http://127.0.0.1:8000/api/v1.0/user/7851171`

# /api/v1.0/hex

GET:

`curl -u dev:dev -i -X GET http://127.0.0.1:8000/api/v1.0/hex/6418073`

POST:

`curl -u dev:dev -i -X POST http://localhost:8000/api/v1.0/hex -H "Content-Type: application/json" -d '{"name": "yvan_hex_1", "owner_id":434596, "image_path":"http://yvanscher.com/favicon.ico", "user_id":434596}'`

DELETE:

`curl -i -X DELETE http://localhost:8000/api/v1.0/hex/5605321 -u dev:dev`

# /api/v1.0/link

GET:

`curl -u dev:dev -i -X GET http://127.0.0.1:8000/api/v1.0/link/7059414`

POST:

`curl -u dev:dev -i -X POST -H "Content-Type: application/json" -d '{"url":"yvanscher.com", "description":"a link to yvans personal site", "hex_object_id":"534f6e75-93a6-4b6d-9dcf-85ae20fcb144"}' http://127.0.0.1:8000/api/v1.0/link`

DELETE:

`curl -u dev:dev -i -X DELETE http://127.0.0.1:8000/api/v1.0/link/7059414`

# /api/v1.0/hexlinks

GET:

`curl -u dev:dev -i -X GET http://127.0.0.1:8000/api/v1.0/hexlinks/534f6e75-93a6-4b6d-9dcf-85ae20fcb144`

POST:

`curl -u dev:dev -i -X POST -H "Content-Type: application/json" -d '[{"url":"yvanscher.com", "description":"a link to yvans personal site", "hex_object_id":"534f6e75-93a6-4b6d-9dcf-85ae20fcb144"}, {"url":"yvanscher.com", "description":"a link to yvans personal site", "hex_object_id":"534f6e75-93a6-4b6d-9dcf-85ae20fcb144"}]' http://127.0.0.1:8000/api/v1.0/hexlinks`

DELETE:

`curl -u dev:dev -i -X DELETE http://127.0.0.1:8000/api/v1.0/hexlinks/534f6e75-93a6-4b6d-9dcf-85ae20fcb144`

# /api/v1.0/location

GET:

`curl -u dev:dev -i -X GET http://localhost:8000/api/v1.0/location/534f6e75-93a6-4b6d-9dcf-85ae20fcb144`

POST:

`curl -u dev:dev -i -X POST  http://localhost:8000/api/v1.0/location -H "Content-Type: application/json" -d '{"platform":"ios","location":"myhexlist", "hex_object_id":"534f6e75-93a6-4b6d-9dcf-85ae20fcb144", "user_object_id":"f78f8e39-2235-4238-b930-1d838ffa56e0"}'`

DELETE:

`curl -u dev:dev -i -X DELETE http://localhost:8000/api/v1.0/location/534f6e75-93a6-4b6d-9dcf-85ae20fcb144`

# /api/v1.0/send

GET:

`curl -u dev:dev -i -X GET http://localhost:8000/api/v1.0/send/175823b5-64a1-47d0-a6a6-81f2c685af11`

POST:

`curl -u dev:dev -i -X POST  http://localhost:8000/api/v1.0/send -H "Content-Type: application/json" -d '{"sender_id":"d7c2f463-736f-467e-a317-a6e4b64cd6a6","recipient_id":"9066e9a9-bc47-4f12-8436-551695026421", "hex_object_id":"175823b5-64a1-47d0-a6a6-81f2c685af11"}'`

DELETE:

`curl -u dev:dev -i -X DELETE http://localhost:8000/api/v1.0/send/175823b5-64a1-47d0-a6a6-81f2c685af11`

# using curl

-u username:password is a way ot authenticate to the API. altough you should use a token instead. to use a token, first hit the token generation api [endpoint](#/api/v1.0/token), get a token and use it instead of the username (password can be any word w/ a token) like:

`curl -u eyJpYXQiOjE0NjM5NDkyMzksImV4cCI6MTQ2NDAzNTYzOSwiYWxnIjoiSFMyNTYifQ.eyJpZCI6NTI3NDA3OX0.Tc_0outiJw1xIXFWO1HTyYhFXR9oh4h1eLVoYPHEke:whatever`

creating a user already requires the existence of a user, to get around this. on a live DB just copy a local DB entry and manually insert it into heroku postgres, once that's done you can use that user to generate tokens make yous password a long unhackable phrase (at least 4-5 words, some numbers, and special chars). you can manually insert this user onto the staging server like so: .

# running locally

launch redis
`launchctl load ~/Library/LaunchAgents/homebrew.mxcl.redis.plist`

stop redis
`launchctl unload ~/Library/LaunchAgents/homebrew.mxcl.redis.plist`

craete postgres folder if not created:
`initdb /usr/local/var/postgres/`

start postgres locally
`pg_ctl start -D /usr/local/var/postgres/`

`createuser --pwprompt USER_NAME`

`createdb -O admin -E utf8 DB_NAME`

start the server
`make run` or `gunicorn hexlistserver.app:app`

start the worker in another tab (or background process)
`python hexlistserver/worker.py`

do stuff

# development

1 - Clone hexlistserver repository

2 - Add Heroku remotes for staging & production

`git remote add stage https://git.heroku.com/hexlistserver-stage.git`

`git remote add prod https://git.heroku.com/hexlistserver-prod.git`

3 - Install Postgressql locally

`brew install postgresql`

4 - Create hexlistserver conda env from environment.yml

`conda env create -f environment.yml`

5 - Start postgresql and create a database user and the hexlistserver database

start postgres locally
`pg_ctl start -D /usr/local/var/postgres/`

`createuser --pwprompt admin`

`createdb -O admin -E utf8 hexlistserver`

`psql -U admin -W hexlistserver`

6 - Set ENV variables for hexlistserver app

`heroku config --remote stage`

Copy all values except APP_SETTINGS and DATABASE_URL, and do not set USER_MAKER_PASSWORD yet.

`export ANON_USER_ID= && export ANON_USER_NAME= && export ANON_USER_PASSWORD= && export APP_SETTINGS=hexlistserver.config.DevelopmentConfig && export DATABASE_URL=postgresql://localhost/hexlistserver && export FLASK_SECRET_KEY= && export POSTMARK_API_KEY= && export POSTMARK_API_TOKEN= && export POSTMARK_INBOUND_ADDRESS= && export POSTMARK_SMTP_SERVER= && export USER_MAKER_NAME= && export USER_MAKER_PASSWORD=`

7 - Run `make upgrade` to perform migration & create database tables

8 - Create 'user-maker' and 'anon' users

Log in to staging server's database

`heroku pg:psql --remote stage --app hexlistserver-stage`

`SELECT * FROM user_objects;`

Copy id, name, and password hash of stage server's 'user-maker' and 'anon' users

Create new user-maker user locally

INSERT INTO user_objects VALUES ('USER_ID','USER_NAME','USER_PASSWORD_HASH');

9 - Test locally by running `make run` then [test the feature with postman](https://www.getpostman.com/).

10 - run unit tests

11 - then upload to staging heroku and tests feature

12 - then once you're sure it works upload to prodduction heroku 'git push https://git.heroku.com/hexlistserver-prod.git master', i dont add a second remote because 1, we should be careful bout what we push to prod, 2, heroku is a lot less verbose when there's one remote.

`get redis instance locally` (for the worker that gathers link info):

install
`brew install redis`

tell launchtl to manage redis
`ln -sfv /usr/local/opt/redis/*.plist ~/Library/LaunchAgents`

add redis on heroku
`heroku addons:create redistogo`

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

run `source env.sh` to setup local env variables properly, any environment variables that are not loaded from this file can be found in the environment on the staging or prod servers.

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
ANON_USER_ID:        USRID
ANON_USER_NAME:      BLAH
ANON_USER_PASSWORD:  PWD
APP_SETTINGS:        hexlistserver.config.DevelopmentConfig
FLASK_SECRET_KEY:    SECRET
DATABASE_URL: postgres://postgresuser:password@ec2ipaddr.compute-1.amazonaws.com:PORT/DBNAME
USER_MAKER_NAME:     USR
USER_MAKER_PASSWORD: PWD
```

migrating the db on herkou:

```
# make sure all environment variables are properly set on the heroku instance
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

restoring the db from a local copy:

1 - get credentials (the database url):

`heroku pg:credentials --remote prod`

2 - use pg_restore:

`pg_restore -d 'THE_URL_FROM_STEP_1' LOCAL_BACKUP_FILE_PATH`

# setup

python flask app

postgresdb with flask-sqlalchemy

heroku hosting and heroku postgres db

# backups

currently i have a backup scheduled as so:

```
heroku pg:backups schedule DATABASE_URL --at '04:00 America/New_York' --remote prod
```

4 AM New York time every day we do a backup. as per [heroku docs](https://devcenter.heroku.com/articles/heroku-postgres-backups#scheduled-backups-retention-limits) this daily backup replaces the old daily backup everyday, we only store one most recent copy per week.

it is also advisable that a programmer do a manual backup (of which 5 can be stored) at monday at noon like so:

```
heroku pg:backups capture --remote prod
```

# resources

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

[how to - flask migrate](https://www.youtube.com/watch?v=YJibNSI-iaE)

[how to actually use alembic because the manager script is shit](http://www.chesnok.com/daily/2013/07/02/a-practical-guide-to-using-alembic/)

[docs for ops for alembic](http://alembic.zzzcomputing.com/en/latest/ops.html)

[heroku Procfile](https://devcenter.heroku.com/articles/procfile)

[heroku config vars](https://devcenter.heroku.com/articles/config-vars)

[psql shell guide](http://postgresguide.com/utilities/psql.html)

[psycopg docs](http://initd.org/psycopg/docs/)

[http verbs](http://www.restapitutorial.com/lessons/httpmethods.html)

[reading about heroku gunicorn workers](https://devcenter.heroku.com/articles/python-gunicorn#basic-configuration)

[flask session tutorial](http://www.tutorialspoint.com/flask/flask_sessions.htm)

[flask session docs](https://pythonhosted.org/Flask-Session/)

[jinja docs](http://jinja.pocoo.org/docs/dev/templates/)

[python rq docs](http://python-rq.org/docs/) -> for managing redis queues and ous scraper

[tutorial on how to run the web scraper on heroku worker dyno](https://devcenter.heroku.com/articles/python-rq)

[flask update row info](http://stackoverflow.com/questions/6699360/flask-sqlalchemy-update-a-rows-information)

[heroku add custom domain](https://devcenter.heroku.com/articles/custom-domains)

[twilio addon custom verification](https://www.twilio.com/docs/tutorials/walkthrough/account-verification/python/flask)

[point namecheap to heroku app](https://www.namecheap.com/support/knowledgebase/article.aspx/9737/2208/how-to-point-a-domain-to-the-heroku-app)

[generated terms here](http://www.bennadel.com/coldfusion/privacy-policy-generator.htm#primary-navigation)

[database backups](https://devcenter.heroku.com/articles/heroku-postgres-backups)

# author

[yvan](https://github.com/yvan)
