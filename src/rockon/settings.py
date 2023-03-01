"""
Django settings for rockon project.

Generated by 'django-admin startproject' using Django 4.1.4.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.1/ref/settings/
"""

from __future__ import annotations

from os import getenv, path
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv("DJANGO_SECRET_KEY", "changeme")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = getenv("DJANGO_DEBUG", False) == "True"

ALLOWED_HOSTS = getenv("DJANGO_ALLOWED_HOSTS", "localhost").split(" ")

INTERNAL_IPS = getenv("DJANGO_INTERNAL_IPS", "127.0.0.1").split(" ")

APP_BUILD_DATE = getenv("DJANGO_BUILD_DATE", "now")
APP_BUILD_HASH = getenv("DJANGO_BUILD_HASH", "local-dev")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_q",
    "bands.apps.BandsConfig",
    "crew.apps.CrewConfig",
    "crm.apps.CrmConfig",
    "event.apps.EventConfig",
    "exhibitors.apps.ExhibitorsConfig",
    "tools.apps.ToolsConfig",
]

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "crm.magic_link_auth.MagicLinkAuth",
]

if DEBUG:
    MIDDLEWARE.insert(2, "debug_toolbar.middleware.DebugToolbarMiddleware")

ROOT_URLCONF = "rockon.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "rockon.context_processors.app_info.get_build_date",
                "rockon.context_processors.app_info.get_build_hash",
            ],
        },
    },
]

WSGI_APPLICATION = "rockon.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": getenv("POSTGRES_HOST"),
        "NAME": getenv("POSTGRES_DB"),
        "PASSWORD": getenv("POSTGRES_PASSWORD"),
        "PORT": getenv("POSTGRES_PORT"),
        "USER": getenv("POSTGRES_USER"),
    },
}

if getenv("DJANGO_USE_SQLITE", False) == "True":
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": path.join(BASE_DIR, "_db/db.sqlite3"),
    }

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}

Q_CLUSTER = {
    "name": "DJRedis",
    "workers": 4,
    "retry": 60,
    "timeout": 30,
    "django_redis": "default",
}

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.ScryptPasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Berlin"

USE_I18N = True

USE_TZ = True


# Mail settings
# https://docs.djangoproject.com/en/4.1/topics/email/
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = getenv("DJANGO_EMAIL_HOST", "localhost")
EMAIL_PORT = getenv("DJANGO_EMAIL_PORT", 25)
EMAIL_HOST_USER = getenv("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = getenv("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = getenv("DJANGO_EMAIL_USE_TLS", False) == "True"
EMAIL_USE_SSL = getenv("DJANGO_EMAIL_USE_SSL", False) == "True"
DEFAULT_FROM_EMAIL = getenv("DJANGO_DEFAULT_FROM_EMAIL", "webmaster@localhost")
EMAIL_SUBJECT_PREFIX = getenv("DJANGO_EMAIL_SUBJECT_PREFIX", "[Rockon] ")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/

STATIC_URL = getenv("DJANGO_STATIC_URL", "static/")

STATIC_ROOT = path.join(BASE_DIR, "dist")

STATICFILES_DIRS = [
    path.join(BASE_DIR, "static"),
]

MEDIA_ROOT = getenv("DJANGO_MEDIA_ROOT", "uploads/")
MEDIA_URL = getenv("DJANGO_MEDIA_URL", "uploads/")

DOMAIN = getenv("DJANGO_DOMAIN", "http://localhost:8000/")

LOGIN_URL = "crm_request_magic_link"
LOGIN_REDIRECT_URL = "crm_user_profile"
LOGOUT_REDIRECT_URL = "crm_logout"


# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "formatters": {
        "default": {"format": "%(asctime)s %(levelname)s %(module)s: %(message)s"},
    },
    "root": {
        "handlers": ["console"],
        "level": getenv("DJANGO_LOG_LEVEL", "INFO"),
    },
}

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly"
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}
