"""
PYTHON 3.9+
Django settings for Django_Online_Shop project.

Generated by 'django-admin startproject' using Django 3.2.8.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

from pathlib import Path
import os
import django_heroku
import cloudinary
from . import secrets

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = secrets.SECRET_KEY

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = secrets.DEBUG

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary_storage',
    'django.contrib.staticfiles',
    'whitenoise.runserver_nostatic',
    # removed because caused some errors
    #'django.contrib.sites',
    'cloudinary',
    'catalog.apps.CatalogConfig',
    'layout',
    'accounts',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',

    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # my profiling middleware
    #'catalog.middleware.profiling_middleware',
]



ROOT_URLCONF = 'Django_Online_Shop.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates']
        ,
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Django_Online_Shop.wsgi.application'


# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases

DATABASES = secrets.DATABASES


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.2/howto/static-files/


STATIC_ROOT = os.path.join(BASE_DIR, 'static_root/')
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
    ("catalog", 'catalog/static')
)

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

API_SECRET = os.environ.get('cloudinary_secret', None)

if API_SECRET:
    cloudinary.config(
        cloud_name="dcf7zq0mn",
        api_key="928634439619496",
        api_secret=API_SECRET,
    )
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': 'dcf7zq0mn',
        'API_KEY': '928634439619496',
        'API_SECRET': API_SECRET,
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_USE_TLS = secrets.EMAIL_USE_TLS
EMAIL_HOST = secrets.EMAIL_HOST
EMAIL_HOST_USER = secrets.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = secrets.EMAIL_HOST_PASSWORD
EMAIL_PORT = secrets.EMAIL_PORT


MAILCHIMP_API_KEY = secrets.MAILCHIMP_API_KEY
MAILCHIMP_DATA_CENTER = secrets.MAILCHIMP_DATA_CENTER
MAILCHIMP_EMAIL_LIST_ID = secrets.MAILCHIMP_EMAIL_LIST_ID
# FOR INITIALIZING NEW DATABASE
DB_TRANSFER = False

# Settings for git-flow principle (merging)
if DEBUG == False:
    """
    DISABLED BECAUSE
    
    Deployed on Heroku free Dyno
    Means no SSL certificate can be installed
    The Server works through Cloudflare flexible
    In such condition these settings make infinite redirects
    
    """
    #CSRF_COOKIE_SECURE = True
    #SESSION_COOKIE_SECURE = True
    #SECURE_SSL_REDIRECT = True
    #SECURE_HSTS_SECONDS = 1
    #SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    #SECURE_HSTS_PRELOAD = True
    ALLOWED_HOSTS = ['autoy.pp.ua','autoyshop.pp.ua', 'autoy.herokuapp.com', 'localhost']
    #if DB_TRANSFER:
    #    INSTALLED_APPS += ['silk']
    #    MIDDLEWARE.insert(3, 'silk.middleware.SilkyMiddleware')
else:
    ALLOWED_HOSTS = []
    #INSTALLED_APPS += ['silk']
    #MIDDLEWARE.insert(3, 'silk.middleware.SilkyMiddleware')


django_heroku.settings(locals())

