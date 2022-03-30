#DEFAULT_SECRET_KEY = 'django-insecure-w1&xd4@!-_5l$yv5e=d1n80nolz1-)ioi__unf^*op*w3v^tww'
import os
import dj_database_url

SECRET_KEY = 'vd3=yu5t#(h62ufy6i@&w7z$9^iv$=+)yaovlx@1d11q03l(g9'

EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'dzhyguntestemail@gmail.com'
EMAIL_HOST_PASSWORD = 't!2hGibA5qKhiMg'
EMAIL_PORT = 587

DEBUG = True if os.environ.get("DEBUG", False) else False

MAILCHIMP_API_KEY = "f140bc98a01f550de5ca4293b38f26b7-us20"
MAILCHIMP_DATA_CENTER = "us20"
MAILCHIMP_EMAIL_LIST_ID = "5cf8bd51b5"


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'test',
        'USER': 'autoyadmin',
        'PASSWORD': 'autoyadmin2021',
        'HOST': 'localhost',
        'PORT': '',
    }
}

db_from_env = dj_database_url.config(conn_max_age=600)
DATABASES['default'].update(db_from_env)

