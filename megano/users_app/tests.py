import os

from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from django.urls import reverse

from megano import settings
from users_app.models import Profile


class SignInViewTestCase(APITestCase):
    """Тест представления для аутентификации существующего пользователя. Родитель: APITestCase."""

    def setUp(self) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        self.credentials = dict(username='test_user', password='test_password')
        self.user = User.objects.create_user(**self.credentials)

    def tearDown(self) -> None:
        """Метод для очистки БД после проведения теста."""

        self.user.delete()

    def test_sign_in(self) -> None:
        """Метод для тестирования аутентификации существующего пользователя."""

        response = self.client.post(
            reverse('login'),
            self.credentials,
        )
        self.assertEqual(response.status_code, 200)


class SignUpViewTestCase(APITestCase):
    """Тест представления для регистрации нового пользователя. Родитель: APITestCase."""

    def setUp(self) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        User.objects.filter(username='test_username').delete()
        Profile.objects.filter(user__username='test_username').delete()

    def test_sign_up(self) -> None:
        """Метод для тестирования регистрации нового пользователя."""

        response = self.client.post(
            reverse('register'),
            {
                'name': 'test_name',
                'username': 'test_username',
                'password': 'test_password'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            User.objects.filter(username='test_username').exists()
        )
        self.assertTrue(
            Profile.objects.filter(
                fullName='test_name',
                user__username='test_username'
            ).exists()
        )


class SignOutViewTestCase(APITestCase):
    """Тест представления для выхода из учетной записи авторизованного пользователя. Родитель: APITestCase."""

    def test_logout(self) -> None:
        """Метод для тестирования выхода из учетной записи авторизованного пользователя."""

        response = self.client.post(
            reverse('logout')
        )
        self.assertEqual(response.status_code, 200)


class ProfileViewTestCase(APITestCase):
    """Тест представления для просмотра и редактирования профиля пользователя. Родитель: APITestCase."""

    @classmethod
    def setUpClass(cls) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        cls.credentials = dict(username='test_user', password='test_password')
        cls.user = User.objects.create_user(**cls.credentials)
        cls.profile = Profile.objects.create(
            user=cls.user,
            fullName='test_name',
        )

    @classmethod
    def tearDownClass(cls) -> None:
        """Метод для очистки БД после проведения теста."""

        cls.user.delete()
        cls.profile.delete()

    def setUp(self) -> None:
        """Метод для предварительной подготовки БД к проведению теста."""

        self.client.login(**self.credentials)

    def test_profile_detail(self) -> None:
        """Метод для тестирования просмотра профиля пользователя."""

        response = self.client.get(
            reverse('profile_detail')
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.profile.fullName)

    def test_profile_detail_not_authenticated(self) -> None:
        """Метод для тестирования просмотра профиля пользователя неаутентифицированным пользователем."""
        self.client.logout()
        response = self.client.get(
            reverse('profile_detail')
        )
        self.assertEqual(response.status_code, 403)

    def test_profile_update(self) -> None:
        """Метод для тестирования редактирования профиля пользователя."""

        response = self.client.post(
            reverse('profile_detail'),
            {
                'fullName': 'new_test_name',
                'email': 'test@email.ru',
                'phone': '1234567890'
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'new_test_name')
        self.assertContains(response, 'test@email.ru')
        self.assertContains(response, '1234567890')

    def test_profile_update_not_authenticated(self) -> None:
        """Метод для тестирования редактирования профиля пользователя неаутентифицированным пользователем."""

        self.client.logout()
        response = self.client.post(
            reverse('profile_detail'),
            {
                'fullName': 'new_test_name',
                'email': 'test@email.ru',
                'phone': '1234567890'
            }
        )
        self.assertEqual(response.status_code, 403)

    def test_user_password_update(self) -> None:
        """Метод для тестирования обновления пароля пользователя."""

        response = self.client.post(
            reverse('password_update'),
            {
                'currentPassword': self.credentials['password'],
                'newPassword': 'new_test_password'
            }
        )
        self.assertEqual(response.status_code, 200)

    def test_user_password_update_not_authenticated(self) -> None:
        """Метод для тестирования обновления пароля пользователя неаутентифицированным пользователем."""

        self.client.logout()
        response = self.client.post(
            reverse('password_update'),
            {
                'currentPassword': self.credentials['password'],
                'newPassword': 'new_test_password'
            }
        )
        self.assertEqual(response.status_code, 403)

    def test_user_avatar_update(self) -> None:
        """Метод для тестирования обновления аватара пользователя."""

        avatar_file = os.path.join(settings.MEDIA_ROOT / 'avatars', 'test_avatar.jpg')
        with open(avatar_file, 'rb') as avatar:
            response = self.client.post(
                reverse('avatar_update'),
                {
                    'avatar': avatar
                },
                format='multipart',
            )
            self.assertEqual(response.status_code, 200)

    def test_user_avatar_update_not_authenticated(self) -> None:
        """Метод для тестирования обновления аватара пользователя неаутентифицированным пользователем."""

        self.client.logout()
        avatar_file = os.path.join(settings.MEDIA_ROOT / 'avatars', 'test_avatar.jpg')
        with open(avatar_file, 'rb') as avatar:
            response = self.client.post(
                reverse('avatar_update'),
                {
                    'avatar': avatar
                },
                format='multipart',
            )
            self.assertEqual(response.status_code, 403)