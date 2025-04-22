import os
from livekit import api
from dotenv import load_dotenv

load_dotenv()


def generate_livekit_token(identity, channel_uuid):
    """
    Генерирует JWT-токен для подключения к LiveKit-комнате с UUID канала.
    """
    token = api.AccessToken(os.getenv('LIVEKIT_API_KEY'), os.getenv('LIVEKIT_API_SECRET')) \
        .with_identity(identity) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=channel_uuid,  # UUID канала как имя комнаты
            can_publish=True,
            can_subscribe=True
        ))
    return token.to_jwt()
