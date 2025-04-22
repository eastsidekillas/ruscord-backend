from django.contrib import admin
from .models import Server, Member, InviteLink

# Register your models here.
admin.site.register(Server)
admin.site.register(Member)
admin.site.register(InviteLink)