from django.db.migrations import serializer
from django.template.defaulttags import url
from rest_framework import serializers
from users_app.models import Avatar, Profile


class AvatarSerializer(serializers.ModelSerializer):
    """Сериалайзер модели аватара пользователя. Родитель: ModelSerializer."""

    src = serializers.SerializerMethodField()

    class Meta:
        model = Avatar
        fields = ["src", "alt"]

    def get_src(self, obj: Avatar) -> url:
        """Метод для получения ссылки на изображение аватара пользователя."""

        return obj.src.url


class ProfileSerializer(serializers.ModelSerializer):
    """Сериалайзер модели профиля. Родитель: ModelSerializer."""

    avatar = AvatarSerializer(read_only=True)

    class Meta:
        model = Profile
        fields = ["fullName", "email", "phone", "avatar"]


class UserPasswordSerializer(serializers.BaseSerializer):
    """Сериалайзер пароля пользователя. Родитель: BaseSerializer."""

    def to_internal_value(self, data: dict) -> dict:
        """Метод для получения данных (текущего и нового пароля пользователя) и валидации."""

        currentPassword = data.get("currentPassword")
        newPassword = data.get("newPassword")
        user = self.instance
        if not user.check_password(currentPassword):
            raise serializers.ValidationError(
                "Введенные текущий пароль и пароль не совапдают!"
            )
        return {"currentPassword": currentPassword, "newPassword": newPassword}

    def update(self, instance: serializer, validated_data: dict) -> serializer:
        """Метод для обновления пароля пользователя."""

        new_password = validated_data.get("newPassword")
        instance.set_password(new_password)
        instance.save(update_fields=["password"])
        return instance
