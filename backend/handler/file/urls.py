from django.urls import path, include
from rest_framework import routers
from backend.handler.file import file, file_group
# 联系人分组
group_router = routers.DefaultRouter()
group_router.register(r'file/group', file_group.FileGroupViewSet, basename='file_group')
# 联系人
router = routers.DefaultRouter()
router.register(r'file', file.FileViewSet, basename='file')
urlpatterns = (
    # 文件分组
    path('', include(group_router.urls)),


    # 文件管理
    path('', include(router.urls))
)