from django.core.cache import cache
from app_users.models import Profile
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

STATUS_KEY = "user_status:{}"
STATUS_TTL = 300  # 5 минут


@database_sync_to_async
def _get_profile(user_id):
    try:
        return Profile.objects.get(user_id=user_id)
    except Profile.DoesNotExist:
        return None


@database_sync_to_async
def _save_profile(profile):
    profile.save()


@sync_to_async
def _set_status_cache(user_id, status):
    cache.set(STATUS_KEY.format(user_id), status, timeout=STATUS_TTL)


@sync_to_async
def _get_status_cache(user_id):
    return cache.get(STATUS_KEY.format(user_id))


async def set_user_status(user_id, status):
    # Обновляем базу данных
    profile = await _get_profile(user_id)
    if profile:
        profile.status = status
        await _save_profile(profile)

    # Обновляем Redis
    await _set_status_cache(user_id, status)


async def get_user_status(user_id):
    # Сначала пробуем из Redis
    status = await _get_status_cache(user_id)
    if status:
        return status

    # Если нет — пробуем из базы
    profile = await _get_profile(user_id)
    if profile:
        return profile.status

    return "offline"


async def set_user_offline(user_id):
    profile = await _get_profile(user_id)
    if profile:
        profile.status = "offline"
        await _save_profile(profile)
    await _set_status_cache(user_id, "offline")
