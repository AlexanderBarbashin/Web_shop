# Generated by Django 4.2.2 on 2023-07-09 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0010_alter_avatar_src'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avatar',
            name='src',
            field=models.ImageField(upload_to='avatars/user_avatars/', verbose_name='Ссылка'),
        ),
    ]
