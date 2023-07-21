from django.contrib import admin

from users_app.models import Avatar, Profile


class AvatarAdmin(admin.ModelAdmin):
    """Класс для администрирования модели аватара. Родитель: ModelAdmin."""

    list_display = 'pk', 'src', 'alt'


class ProfileAdmin(admin.ModelAdmin):
    """Класс для администрирования модели профиля пользователя. Родитель: ModelAdmin."""

    list_display = 'pk', 'user', 'fullName', 'email', 'phone', 'balance', 'avatar'


admin.site.register(Avatar, AvatarAdmin)

admin.site.register(Profile, ProfileAdmin)