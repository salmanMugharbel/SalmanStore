from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0004_userprofile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]
