"""
Django settings for rockon project.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from __future__ import annotations

from os import getenv, path
from pathlib import Path

import sentry_sdk
from environs import Env
from sentry_sdk.integrations.django import DjangoIntegration

env = Env()

# read .env file, if it exists
env.read_env()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost"])

INTERNAL_IPS = env.list("DJANGO_INTERNAL_IPS", default=["127.0.0.1"])

APP_BUILD_DATE = env.str("BUILD_DATE", default="now")
APP_BUILD_HASH = env.str("GITHUB_SHA", default="local-dev")

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_q",
    "corsheaders",
    "rest_framework",
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
    "corsheaders.middleware.CorsMiddleware",
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
                "rockon.context_processors.sentry_frontend.get_sentry_data",
                "rockon.context_processors.get_domain.get_domain",
            ],
        },
    },
]

WSGI_APPLICATION = "rockon.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": path.join(BASE_DIR, "_db/db.sqlite3"),
    },
}

# Redis
with env.prefixed("REDIS_"):
    REDIS_HOST = env.str("HOST", default="localhost")
    REDIS_PORT = env.str("PORT", default="6379")
    REDIS_DB = env.str("DB", default="0")

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
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
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Berlin"

USE_I18N = True

USE_TZ = True

with env.prefixed("DJANGO_EMAIL_"):
    # Mail settings
    # https://docs.djangoproject.com/en/4.2/topics/email/
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST = env.str("HOST", default="localhost")
    EMAIL_PORT = env.str("PORT", default="25")
    EMAIL_HOST_USER = env.str("HOST_USER", default="user")
    EMAIL_HOST_PASSWORD = env.str("HOST_PASSWORD", default="password")
    EMAIL_USE_TLS = env.bool("USE_TLS", default=False)
    EMAIL_USE_SSL = env.bool("USE_SSL", default=False)
    EMAIL_DEFAULT_FROM = env.str("DEFAULT_FROM", default="webmaster@localhost")
    EMAIL_SUBJECT_PREFIX = env.str("SUBJECT_PREFIX", default="[Rockon]")

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = env("DJANGO_STATIC_URL", "static/")

STATIC_ROOT = path.join(BASE_DIR, "dist")

STATICFILES_DIRS = [
    path.join(BASE_DIR, "static"),
]

with env.prefixed("DJANGO_MEDIA_"):
    MEDIA_ROOT = env.str("ROOT", default="uploads/")
    MEDIA_URL = env.str("URL", default="uploads/")

DATA_UPLOAD_MAX_MEMORY_SIZE = 26214400

DOMAIN = env.str("DJANGO_DOMAIN", default="http://localhost:8000")

with env.prefixed("DJANGO_CORS_"):
    CORS_ALLOWED_ORIGINS = env.list(
        "ALLOWED_ORIGINS", default=["http://localhost:8000"]
    )
    # CORS_ALLOWED_ORIGIN_REGEXES = env.list("ALLOWED_ORIGIN_REGEXES", default=[])
    if DEBUG:
        CORS_ORIGIN_ALLOW_ALL = env.bool("ORIGIN_ALLOW_ALL", default=False)

LOGIN_URL = "crm_request_magic_link"
LOGIN_REDIRECT_URL = "crm_user_profile"
LOGOUT_REDIRECT_URL = "crm_logout"


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

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
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

with env.prefixed("SENTRY_"):
    SENTRY_ENABLED = env.bool("ENABLED", default=False)
    SENTRY_ENABLED_FRONTEND = env.bool("ENABLED_FRONTEND", default=False)
    SENTRY_DSN = env.str("DSN", default=None)
    SENTRY_ENVIRONMENT = env.str("ENVIRONMENT", default="dev")
    SENTRY_TRACES_SAMPLE_RATE = env.float("TRACES_SAMPLE_RATE", default="1.0")
    SENTRY_SEND_DEFAULT_PII = env.bool("SEND_DEFAULT_PII", default=False)

if SENTRY_ENABLED and SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(),
        ],
        environment=SENTRY_ENVIRONMENT,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for performance monitoring.
        # We recommend adjusting this value in production.
        traces_sample_rate=SENTRY_TRACES_SAMPLE_RATE,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=SENTRY_SEND_DEFAULT_PII,
    )

FFMPEG_BIN = env.str("FFMPEG_BIN", default="ffmpeg")
CONVERT_BIN = env.str("CONVERT_BIN", default="convert")
