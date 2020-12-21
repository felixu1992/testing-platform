from django.urls import path, include
from rest_framework import routers
from backend.handler.case import case_info

# 用例
case_router = routers.DefaultRouter()
case_router.register(r'', case_info.CaseInfoViewSet, basename='case')