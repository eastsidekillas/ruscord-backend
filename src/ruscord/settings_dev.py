from .settings_base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# HTTP-совместимые куки для локальной разработки
# (secure=True работает только на HTTPS)
SIMPLE_JWT["COOKIE_SETTINGS"]["ACCESS_TOKEN"]["secure"] = False
SIMPLE_JWT["COOKIE_SETTINGS"]["ACCESS_TOKEN"]["samesite"] = "Lax"
SIMPLE_JWT["COOKIE_SETTINGS"]["REFRESH_TOKEN"]["secure"] = False
SIMPLE_JWT["COOKIE_SETTINGS"]["REFRESH_TOKEN"]["samesite"] = "Lax"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {
            'format': '[{levelname}] {name}: {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'app_gateway': {'level': 'DEBUG'},
        'django': {'level': 'INFO'},
    },
}