import os
from livekit import api
from django.conf import settings


def generate_livekit_token(identity, channel_id, video_grants=None, metadata=None):
    """
    Генерирует JWT-токен для подключения к LiveKit-комнате.

    Args:
        identity (str): Уникальный идентификатор пользователя.
        channel_id (str): Идентификатор комнаты LiveKit (обычно ID канала).
        video_grants (api.VideoGrants, optional): Права доступа к видео.
                                                  Defaults to стандартные права.
    """
    token = api.AccessToken(settings.LIVEKIT_API_KEY, settings.LIVEKIT_API_SECRET) \
        .with_identity(identity)

    if metadata:
        token.with_metadata(metadata)

    if video_grants:
        token.with_grants(video_grants)
    else:
        token.with_grants(api.VideoGrants(
            room_join=True,
            room=channel_id,
            can_publish=True,
            can_subscribe=True
        ))

    return token.to_jwt()
