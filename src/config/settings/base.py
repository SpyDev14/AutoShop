"""
For more information on this file, see
https://docs.djangoproject.com/en/5.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.2/ref/settings/
"""

from pathlib import Path
from environ import Env

import admin_registrar.logging

from src.shared.console.ansi import *


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

Env.read_env(BASE_DIR / ".env")  # парсит .env в os.environ
env = Env()

INTERNAL_IPS = ["127.0.0.1", "localhost"]

# Application definition
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    "django.contrib.sites",
    # Libs
    # Project
    "src.apps.feedback",
    # Libs (req. bottom position)
    "django_cleanup",
]

MIDDLEWARE = [
    # Django
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "src.config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "src.config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
# env.db() использует DATABASE_URL и поддерживает и postgres, и SQLite
DATABASES = {"default": env.db(default="sqlite:///db.sqlite3")}  # type: ignore[reportArgumentType]

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators
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

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/
LANGUAGE_CODE = "ru-RU"
TIME_ZONE = "Europe/Samara"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "static"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Logging
_logs_path = Path(env.str("LOGS_DIR", "logs"))  # type: ignore[reportArgumentType]
LOGS_DIR = BASE_DIR / _logs_path if not _logs_path.is_absolute() else _logs_path

if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(parents=True)


def get_logging_conf(*, debug: bool) -> dict[str, object]:
    debug_level = "DEBUG" if debug else "INFO"
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "[{levelname}] {asctime} {name}:{lineno} {funcName}() {message}",
                "style": "{",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "django-console": {
                "format": "[{levelname}] %s{name}%s: {message}" % (D_GREEN, RESET),
                "style": "{",
            },
            "level-only": {"format": "[{levelname}] {message}", "style": "{"},
            "AdminRegistrar": admin_registrar.logging.RECOMMENDED_FORMATTER,
        },
        "handlers": {
            "console": {
                "level": debug_level,
                "class": "logging.StreamHandler",
                "formatter": "default",
            },
            "file": {
                "level": "INFO",
                "class": "logging.FileHandler",
                "formatter": "default",
                "filename": LOGS_DIR / f"logs.log",
            },
            "django-console": {
                "level": debug_level,
                "class": "logging.StreamHandler",
                "formatter": "django-console",
            },
            "AdminRegistrar": {
                "level": debug_level,
                "class": "logging.StreamHandler",
                "formatter": "AdminRegistrar",
            },
        },
        "root": {"handlers": ["console", "file"], "level": debug_level},
        "loggers": {
            "admin_registrar.registrars": {
                "handlers": ["AdminRegistrar"],
                "level": debug_level,
                "propagate": False,
            },
            "django": {
                "handlers": ["django-console", "file"],
                "level": "INFO",
                "propagate": False,
            },
            # Чтобы не спамил всякой DEBUG ерундой
            "debug_toolbar.store": {"level": "INFO"},
        },
    }


# MARK: EMail-s
EMAIL_BACKEND = "djcelery_email.backends.CeleryEmailBackend"
CELERY_EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env.str("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env.str("EMAIL_HOST_PASSWORD")

# MARK: Libs
SOLO_CACHE = "default"

PHONENUMBER_DEFAULT_REGION = "RU"

TINYMCE_DEFAULT_CONFIG = {
    "height": "25vh",
    "width": "75%",
    "plugins": "advlist,autolink,lists,link,image,charmap,preview,anchor,"
    "searchreplace,visualblocks,code,fullscreen,insertdatetime,media,table,paste,"
    "code,help,wordcount",
    "menubar": "file edit view insert format tools table help",
    "toolbar": "undo redo | formatblocks | bold italic underline strikethrough | removeformat | "
    "alignleft aligncenter alignright alignjustify | "
    "bullist numlist | image media template link | table | code | fullscreen | help",
    "table_toolbar": "tableprops tabledelete | tableinsertrowbefore tableinsertrowafter tabledeleterow | "
    "tableinsertcolbefore tableinsertcolafter tabledeletecol",
}

ADMIN_REGISTRAR = {
    "ADMINS_FOR_MODELS": {
        "solo.models.SingletonModel": "solo.admin.SoloAdmin",
    }
}

# MARK: Project
DOMAIN = "granfort.ru"

NEW_FEEDBACK_REQUEST_EMAIL_NOTIFICATION_RECIPIENTS = ("vlad.buklovsky@gmail.com",)
GET_NEW_FEEDBACK_REQUEST_EMAIL_NOTIFICATION_SENDER_EMAIL = lambda domain: f"noreply@{domain}"
NEW_FEEDBACK_REQUEST_EMAIL_NOTIFICATION_CONTENT_TEMPLATE = "feedback/notification/email.html"
