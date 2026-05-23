import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_messages', '0003_messages_reply_to'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='forwarded_from',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='forwards',
                to='app_messages.messages',
            ),
        ),
    ]