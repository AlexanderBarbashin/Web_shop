# Generated by Django 4.2.2 on 2023-06-25 13:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users_app', '0002_alter_profile_fullname'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='fullName',
            field=models.CharField(blank=True, max_length=150, null=True, verbose_name='Полное имя'),
        ),
    ]