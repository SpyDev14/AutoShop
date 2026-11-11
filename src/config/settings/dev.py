import sys

from src.config.settings.base import *

SECRET_KEY = "SECRET_KEY"

DEBUG = True

MIDDLEWARE = [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    *MIDDLEWARE,
]

ALLOWED_HOSTS = ["*"]

LOGGING = get_logging_conf(debug=DEBUG and "runserver" in sys.argv)
