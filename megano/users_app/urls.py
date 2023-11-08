from django.urls import path
from users_app.views import (
    ProfileView,
    SignInView,
    SignOutView,
    SignUpView,
    UserAvatarUpdateView,
    UserPasswordUpdateView,
)

urlpatterns = [
    path("sign-in", SignInView.as_view(), name="login"),
    path("sign-up", SignUpView.as_view(), name="register"),
    path("sign-out", SignOutView.as_view(), name="logout"),
    path("profile", ProfileView.as_view(), name="profile_detail"),
    path("profile/password", UserPasswordUpdateView.as_view(), name="password_update"),
    path("profile/avatar", UserAvatarUpdateView.as_view(), name="avatar_update"),
]
