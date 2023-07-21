from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields.files import ImageField
from django.db.models.signals import pre_save
from django.dispatch import receiver


def user_avatar_directory_path(instance: 'Avatar', filename: str) -> str:
    """Функция для формирования директории, в которую сохраняются аватары, загруженные пользователем."""

    return 'avatars/user_avatars/{alt}/avatar_{filename}'.format(
        alt=instance.alt,
        filename=filename
    )


def image_size_validate(src: ImageField) -> None:
    """Валидатор аватара пользователя. Запрещает загрузку изображений, размер которых превышает 2 Мб."""

    if src.size / 1048576 > 2:
        raise ValidationError('Размер изображения превышает 2 Мб')


class Avatar(models.Model):
    """Модель аватара пользователя. Родитель: Model."""

    src = models.ImageField(
        upload_to=user_avatar_directory_path,
        default='avatars/default_avatar.gif',
        verbose_name='Ссылка',
        validators=[
            image_size_validate
        ]
    )
    alt = models.CharField(max_length=100, default='Стандартный аватар', verbose_name='Описание')

    class Meta:
        verbose_name = 'Aватар'
        verbose_name_plural = 'Аватары'

@receiver(pre_save, sender=Avatar)
def validate_avatars_src(instance: Avatar, **kwargs) -> None:
    """
    Функция для явного вызова валидатора аватара пользователя перед сохранением нового экземпляра аватара
    пользователя.
    """

    image_size_validate(instance.src)


class Profile(models.Model):
    """Модель профиля пользователя. Родитель: Model."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    fullName = models.CharField(max_length=150, verbose_name='Полное имя')
    email = models.EmailField(null=True, unique=True)
    phone = models.PositiveIntegerField(blank=True, null=True, unique=True, verbose_name='Номер телефона')
    balance = models.DecimalField(decimal_places=2, max_digits=10, default=0, verbose_name='Баланс')
    avatar = models.ForeignKey(Avatar, null=True, on_delete=models.SET_NULL, related_name='profile',
                               verbose_name='Аватар')


    def save(self: 'Profile', **kwargs) -> None:
        """Метод для присвоения стандартного аватара пользователю в случае отсутствия аватара."""

        super().save(**kwargs)
        if not self.avatar:
            avatar = Avatar.objects.create()
            self.avatar = avatar
            self.save(update_fields=['avatar'])

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'
