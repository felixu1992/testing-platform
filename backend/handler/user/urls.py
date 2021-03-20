from rest_framework import routers
from backend.handler.user import user, role

user_router = routers.DefaultRouter()
user_router.register(r'', user.UserViewSet, basename='user')

role_router = routers.DefaultRouter()
role_router.register(r'', role.ProjectViewSet, basename='role')