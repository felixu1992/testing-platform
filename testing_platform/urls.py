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
from django.urls import path
from django.views.generic import TemplateView
from backend.handler.user import user
from backend.handler.contactor import contactor_group
from backend.handler.contactor import contactor
from backend import views

urlpatterns = (
    # 主页
    url(r'^$', TemplateView.as_view(template_name="index.html")),

    # 登录登出
    path('platform/login', user.login),
    path('platform/logout', user.logout),

    # 联系人分组
    path('platform/contactor/group/test', contactor_group.test),
    path('platform/contactor/group/create', contactor_group.create),
    path('platform/contactor/group/delete/<id>', contactor_group.delete),
    path('platform/contactor/group/update', contactor_group.update),
    path('platform/contactor/group/page', contactor_group.page),

    # 联系人
    path('platform/contactor/create', contactor.create),
    path('platform/contactor/delete', contactor.delete),
    path('platform/contactor/update', contactor.update),
    path('platform/contactor/page', contactor.page)
)
