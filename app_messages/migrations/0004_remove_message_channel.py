# Generated by Django 5.1.2 on 2024-12-01 17:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app_messages', '0003_message_channel'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='message',
            name='channel',
        ),
    ]