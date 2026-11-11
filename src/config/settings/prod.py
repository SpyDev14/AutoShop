"""
See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/
"""

from src.config.settings.base import *


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env.str("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

LOGGING = get_logging_conf(debug=DEBUG)
