# Credit API

## About

This is a Rest API developed by Caio Araújo with Python language, using Django and Django REST Framework.

The proposal of this API is to calculate credit loan.

## Requirements
- Python 3.8
- Pipenv (`pip install pipenv`)
- PostgreSQL 12

## Installation

### Dependencies
Install all dependencies listed in `Pipfile` by running:

`pipenv install --dev`

Also provide all environment variables listed in local.env with their respective values.

### Database
In your local PostgreSQL, create a new dabase called `credit`. 
Then, apply the schema by running in the project root:

`python manage.py migrate`

## Running
In the project root run:

`python manage.py runserver`

Once server started, you may access the local server address (check the output of previous command) to check the API documentation

## Tests
To run all test cases, just run in the project root:

`python manage.py test`
