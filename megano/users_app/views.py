import json

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User

from rest_framework import status, permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from users_app.models import Profile, Avatar
from users_app.serializers import ProfileSerializer, UserPasswordSerializer


class SignInView(APIView):
    """Представление для авторизации существующего пользователя. Родитель: APIView."""

    def post(self, request: Request) -> Response:
        """Метод для отправки заполненной формы авторизации существующего пользователя на сервер."""

        user_data = json.loads(request.body)
        username = user_data['username']
        password = user_data['password']
        user = authenticate(request,
                            username=username,
                            password=password)
        if user is not None:
            login(request, user)
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignUpView(APIView):
    """Представление для регистрации нового пользователя. Родитель: APIView."""

    def post(self, request: Request) -> Response:
        """Метод для отправки заполненной формы регистрации нового пользователя на сервер."""

        user_data = json.loads(request.body)
        name = user_data['name']
        username = user_data['username']
        password = user_data['password']
        try:
            user = User.objects.create_user(
                username=username,
                password=password
            )
            Profile.objects.create(
                user=user,
                fullName=name
            )
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SignOutView(APIView):
    """Представление для выхода из учетной записи авторизованного пользователя. Родитель: APIView."""

    def post(self, request: Request) -> Response:
        """Метод для выхода из учетной записи авторизованного пользователя."""

        logout(request)
        return Response(status=status.HTTP_200_OK)


class ProfileView(APIView):
    """Представление для просмотра и редактирования профиля пользователя. Родитель: APIView."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request: Request) -> Response:
        """Метод для просмотра профиля пользователя."""

        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request: Request) -> Response:
        """Метод для редактирования профиля пользователя."""

        profile = Profile.objects.get(user=request.user)
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserPasswordUpdateView(APIView):
    """Представление для обновления пароля пользователя. Родитель: APIView."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Метод для обновления пароля пользователя."""

        user = request.user
        serializer = UserPasswordSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserAvatarUpdateView(APIView):
    """Представление для обновления аватара пользователя. Родитель: APIView."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request: Request) -> Response:
        """Метод для обновления аватара пользователя."""

        user = request.user
        profile = user.profile
        avatar_file = request.FILES.get('avatar')
        try:
            avatar = Avatar.objects.create(
                src=avatar_file,
                alt='{user} аватар'.format(
                    user=user
                )
            )
            profile.avatar = avatar
            profile.save(update_fields=['avatar'])
            return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
