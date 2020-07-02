import dj_database_url

from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ["SECRET_KEY"]

# Database

# https://docs.djangoproject.com/en/3.0/ref/settings/#databases
# dj_database_url docs: https://pypi.org/project/dj-database-url/

DATABASES = {'default': dj_database_url.config(default=os.environ['DATABASE_URL'])}

# Celery configuration
# https://docs.celeryproject.org/en/stable/userguide/configuration.html

CELERY_BROKER_URL = os.environ['BROKER_URL']
CELERY_RESULT_BACKEND = os.environ['BROKER_URL']
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'America/Sao_Paulo'
