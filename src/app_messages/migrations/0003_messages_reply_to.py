import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app_messages', '0002_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='messages',
            name='reply_to',
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='replies',
                to='app_messages.messages',
            ),
        ),
    ]