# Credit API

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
