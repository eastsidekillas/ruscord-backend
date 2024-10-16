from django.contrib import admin
from .models import Friendship, DirectMessage


#отображение даты и прочего в админке джанго
class DirectMessageAdmin(admin.ModelAdmin):
    # Указываем поля, которые должны отображаться в списке сообщений в админке
    list_display = ('sender', 'receiver', 'content', 'created_at', 'edited_at')

    # Поля для фильтрации записей
    list_filter = ('created_at', 'sender', 'receiver')

    # Поля для поиска по сообщениям
    search_fields = ('content', 'sender__username', 'receiver__username')


# Регистрация модели DirectMessage с кастомными настройками

# Register your models here.
admin.site.register(Friendship)
admin.site.register(DirectMessage, DirectMessageAdmin)  #здесь дефолтная модель + написанная модель выше
