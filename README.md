# Credit API

## About

This is a Rest API developed by Caio Araújo with Python language, using Django and Django REST Framework.

The proposal of this API is to calculate credit loan.

## Requirements
- Python 3.8 (https://www.python.org/downloads/)
- Pipenv (`pip install pipenv`)
- PostgreSQL (https://www.postgresql.org/download/)
- Redis (https://redis.io/download)

## Installation

It is highly recommended that you install this project inside a virtual environment (https://docs.python.org/3/library/venv.html).

### Dependencies
Install all dependencies listed in `Pipfile` by running:

`pipenv install --dev`

Also provide all environment variables listed in local.env with their respective values.

### Database
In your PostgreSQL instance, create a new dabase called `credit`. 
Then, apply the schema by running in the project root:

`python manage.py migrate`

## Running

### Celery broker (Redis)
Make sure to run redis-server and configure its URL in `BROKEN_URL` envvar.
To run redis-server, go to redis folder and run:

`src/redis-server`

### Database
Make sure set up your database and configure its URL in `DATABASE_URL` envvar.

### Web api (this project)

To run this project, in the project root run:

`python manage.py runserver`

Once server started, you may access the local server address (check the output of previous command) to check the API documentation.

## Tests
To run all test cases, just run in the project root:

`python manage.py test`
