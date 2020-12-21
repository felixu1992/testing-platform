from django.urls import path, include
from rest_framework import routers
from backend.handler.project import project, project_group

# 项目分组
group_router = routers.DefaultRouter()
group_router.register(r'group', project_group.ProjectGroupViewSet, basename='project_group')
# 项目
router = routers.DefaultRouter()
router.register(r'', project.ProjectViewSet, basename='project')
urlpatterns = (
    # 项目分组
    path('', include(group_router.urls)),

    # 项目
    path('', include(router.urls))
)