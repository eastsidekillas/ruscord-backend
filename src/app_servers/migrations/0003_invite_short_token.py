from django.db import migrations, models
import app_servers.models


class Migration(migrations.Migration):

    dependencies = [
        ('app_servers', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitelink',
            name='token',
            field=models.CharField(
                default=app_servers.models.generate_invite_token,
                max_length=64,
                unique=True,
            ),
        ),
    ]