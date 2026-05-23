from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import AnonymousUser


class SafeAuthenticationMiddleware(AuthenticationMiddleware):
    """Wraps Django's AuthenticationMiddleware to handle stale session data gracefully.

    When the user ID stored in the session cannot be converted to the current PK type
    (e.g. old integer ID after migrating to UUIDs), the session is cleared and the
    request proceeds as anonymous instead of raising an AttributeError.
    """

    def process_request(self, request):
        try:
            super().process_request(request)
        except (AttributeError, ValueError):
            request.session.flush()
            request.user = AnonymousUser()
