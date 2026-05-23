import os

DJANGO_ENV = os.getenv("DJANGO_ENV", "dev")

if DJANGO_ENV == "prod":
    from .settings_prod import *
else:
    from .settings_dev import *