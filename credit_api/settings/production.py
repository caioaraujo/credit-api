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
