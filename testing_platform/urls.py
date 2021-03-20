"""testing_platform URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.urls import path, include, re_path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from backend.handler.case.urls import case_router
from backend.handler.record.urls import record_router, report_router
from backend.handler.user.urls import role_router, user_router

schema_view = get_schema_view(
    openapi.Info(
        title='贼牛逼的 API 文档',
        default_version='v1',
        description='别问，反正就是贼牛逼',
        terms_of_service='https://www.baidu.com',
        contact=openapi.Contact(email='326554201@qq.com'),
        license=openapi.License(name='Apache-2.0 License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = (
    re_path(r'^$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    # 登录登出
    path('user/', include(user_router.urls)),

    # 角色
    path('role/', include(role_router.urls)),

    # 联系人
    path('', include('backend.handler.contactor.urls')),

    # 文件
    path('', include('backend.handler.file.urls')),

    # 项目
    path('', include('backend.handler.project.urls')),

    # 用例
    path('case/', include(case_router.urls)),

    # 记录
    path('record/', include(record_router.urls)),

    # 报告
    path('report/', include(report_router.urls)),

    url(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    url(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc')

)
