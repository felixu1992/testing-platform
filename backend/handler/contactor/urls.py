from django.urls import path, include
from rest_framework import routers
from backend.handler.contactor import contactor, contactor_group
# 联系人分组
group_router = routers.DefaultRouter()
group_router.register(r'contactor/group', contactor_group.ContactorGroupViewSet, basename='contactor_group')
# 联系人
router = routers.DefaultRouter()
router.register(r'contactor', contactor.ContactorViewSet, basename='contactor')
urlpatterns = (
    # 联系人分组
    path('', include(group_router.urls)),

    # 联系人
    path('', include(router.urls))
)