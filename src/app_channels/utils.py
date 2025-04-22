from app_channels.models import Channel
from app_users.models import Profile


def get_or_create_dm_channel(user1: Profile, user2: Profile) -> Channel:
    # Сначала ищем уже существующий канал между этими двумя
    existing_channel = Channel.objects.filter(
        scope='DM',
        participants=user1
    ).filter(
        participants=user2
    ).first()

    if existing_channel:
        return existing_channel

    # Если не найден — создаём новый
    channel = Channel.objects.create(
        name=f"DM: {user1.name} & {user2.name}",
        channel_type='TEXT',
        scope='DM',
        is_private=True,
        owner=user1
    )
    channel.participants.set([user1, user2])
    return channel
