from django.urls import path, include
from rest_framework import routers
from backend.handler.user import user

router = routers.DefaultRouter()
router.register(r'', user.UserViewSet, basename='user')
urlpatterns = (
    # 登录登出
    path('', include(router.urls)),
)