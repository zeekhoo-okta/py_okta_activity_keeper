"""
Django settings for timeapp project.

Generated by 'django-admin startproject' using Django 1.10.1.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.10/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.10/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '***REMOVED***'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# Application definition

APP_URL = os.environ.get('APP_URL')

OKTA_API_TOKEN = os.environ.get('OKTA_API_TOKEN')
OKTA_ORG = os.environ.get('OKTA_ORG')

SFDC_URL = os.environ.get('SFDC_URL')
SFDC_API_VERSION = 'v38.0'
SFDC_CLIENT_ID = os.environ.get('SFDC_CLIENT_ID')
SFDC_SECRET = os.environ.get('SFDC_SECRET')
# SFDC_USERNAME = os.environ.get('SFDC_USERNAME')
# SFDC_PASSWORD = os.environ.get('SFDC_PASSWORD')
# SFDC_TOKEN = os.environ.get('SFDC_SECURITY_TOKEN')

CRONOFY_API_URL = 'https://api.cronofy.com/v1'
CRONOFY_AUTH_URL = 'https://app.cronofy.com/oauth'
CRONOFY_CLIENT_ID = os.environ.get('CRONOFY_CLIENT_ID')
CRONOFY_CLIENT_SECRET = os.environ.get('CRONOFY_CLIENT_SECRET')
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_USER_PWD = os.environ.get('MYSQL_USER_PWD')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'calendar_event_app',

    'bootstrap3',
    'django_forms_bootstrap',
    'bootstrap3_datepicker',
    'rest_framework'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'time_app.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['Templates'],
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

WSGI_APPLICATION = 'time_app.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.10/ref/settings/#databases
if 'RDS_DB_NAME' in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.environ['RDS_DB_NAME'],
            'USER': os.environ['RDS_USERNAME'],
            'PASSWORD': os.environ['RDS_PASSWORD'],
            'HOST': os.environ['RDS_HOSTNAME'],
            'PORT': os.environ['RDS_PORT'],
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'django_db_2',
            'USER': MYSQL_USER,
            'PASSWORD': MYSQL_USER_PWD,
        }
    }


# Password validation
# https://docs.djangoproject.com/en/1.10/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.10/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = False

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.10/howto/static-files/
STATICFILES_DIRS = [
    # '/Users/zeekhoo/Projects/PyCharm/py_okta_activity_keeper/static',
    BASE_DIR + '/static',
]
# STATIC_URL = '/static/'


STATIC_URL = '/static/'
# STATIC_ROOT = "static"
