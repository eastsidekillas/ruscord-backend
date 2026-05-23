import os
from .settings_base import *

DEBUG = False

ALLOWED_HOSTS = list(filter(None, [
    os.getenv("PUBLIC_HOST"),
    "localhost",
]))

if not SECRET_KEY:
    raise ValueError("DJANGO_SECRET_KEY не задан. Обязателен для продакшна.")

# Корректная обработка HTTPS через reverse proxy (nginx)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SESSION_COOKIE_SECURE = True

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{asctime} [{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',
    },
    'loggers': {
        'django': {'level': 'WARNING'},
        'app_gateway': {'level': 'INFO'},
    },
}