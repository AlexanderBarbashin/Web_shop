# Generated by Django 4.2.2 on 2023-06-30 16:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0005_profile_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='avatar',
            name='src',
            field=models.ImageField(default='users_app/avatars/IMG_20230401_135728.jpg', upload_to='users_app/avatars/user_avatars/', verbose_name='Ссылка'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='avatar',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='users_app.avatar', verbose_name='Аватар'),
        ),
    ]