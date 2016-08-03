# Hawkeye Challenge

An online code editing, submission, and judging application designed to be used for the University of Iowa ACM chapter's
annual Hawkeye Challenge, a high school programming competition.

## Running locally
```sh
$ sudo pip install -r requirements.txt
$ npm install bower
$ bower install
$ python manage.py migrate
$ python manage.py createsuperuser
$ python manage.py loaddata startercode.json
$ python manage.py loaddata starter_contest.json
$ python manage.py runserver
```

## Deploying to Heroku
```sh
$ git push heroku master
$ heroku run python manage.py migrate
$ heroku run python manage.py collectstatic

# First time only
$ heroku run python manage.py createsuperuser
$ heroku run python manage.py loaddata startercode.json
$ heroku run python manage.py loaddata starter_contest.json
```
