from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.exceptions import NotFound


def error_message_handler(exc, context):
    response = exception_handler(exc, context)

    # Если ошибка NotFound (ошибка 404)
    if isinstance(exc, NotFound):
        # Форматируем ответ в нужном виде
        response.data = {
            "message": "404: Not Found",
            "code": "0"
        }
    return response


def build_absolute_uri(path: str, host: str, scheme: str = "http") -> str:
    if not path.startswith("/"):
        path = "/" + path
    return f"{scheme}://{host}{path}"