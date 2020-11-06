from django.urls import path
from backend.handler.user import user

urlpatterns = (
    # 登录登出
    path('signin', user.login),
    path('signout', user.logout),
)