import json

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User

from rest_framework import status, permissions, serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiParameter, inline_serializer

from users_app.models import Profile, Avatar
from users_app.serializers import ProfileSerializer, UserPasswordSerializer


@extend_schema(
    parameters=[
        OpenApiParameter(name='username', required=True, type=str, description='Имя пользователя'),
        OpenApiParameter(name='password', required=True, type=str, description='Пароль')
    ],
    responses={
        200: OpenApiResponse(description='Успешная аутентификация'),
        500: OpenApiResponse(description='Неверное имя пользователя или пароль')
    }
)
class SignInView(APIView):
    """Представление для аутентификации существующего пользователя. Родитель: APIView."""

    def post(self, request: Request) -> Response:
        """Метод для отправки заполненной формы аутентификации существующего пользователя на сервер."""

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


@extend_schema(
    parameters=[
        OpenApiParameter(name='name', required=True, type=str, description='Имя'),
        OpenApiParameter(name='username', required=True, type=str, description='Имя пользователя'),
        OpenApiParameter(name='password', required=True, type=str, description='Пароль')
    ],
    responses={
        200: OpenApiResponse(description='Регистрация прошла успешно'),
        500: OpenApiResponse(description='Регистрация не выполнена')
    }
)
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


@extend_schema(
    responses={
        200: OpenApiResponse(description='Выполнен выход из учетной записи'),
    }
)
class SignOutView(APIView):
    """Представление для выхода из учетной записи аутентифицированного пользователя. Родитель: APIView."""

    def post(self, request: Request) -> Response:
        """Метод для выхода из учетной записи аутентифицированного пользователя."""

        logout(request)
        return Response(status=status.HTTP_200_OK)


class ProfileView(APIView):
    """Представление для просмотра и редактирования профиля пользователя. Родитель: APIView."""

    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        responses={
            200: ProfileSerializer,
            403: OpenApiResponse(description='Требуется аутентификация'),
        }
    )
    def get(self, request: Request) -> Response:
        """Метод для просмотра профиля пользователя."""

        profile, _ = Profile.objects.get_or_create(user=request.user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request=ProfileSerializer,
        responses={
            200: ProfileSerializer,
            400: OpenApiResponse(description='Редактирование профиля не выполнено'),
            403: OpenApiResponse(description='Требуется аутентификация'),
        }
    )
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

    @extend_schema(
        request=inline_serializer(
            name='UserPasswordSerializer',
            fields={
                'currentPassword': serializers.CharField(),
                'newPassword': serializers.CharField()
            }
        ),
        responses={
            200: OpenApiResponse(description='Пароль успешно обновлен'),
            400: OpenApiResponse(description='Обновление профиля не выполнено'),
            403: OpenApiResponse(description='Требуется аутентификация'),
        }
    )
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

    @extend_schema(
        responses={
            200: OpenApiResponse(description='Аватар успешно обновлен'),
            400: OpenApiResponse(description='Обновление аватара не выполнено'),
            403: OpenApiResponse(description='Требуется аутентификация'),
        }
    )
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
