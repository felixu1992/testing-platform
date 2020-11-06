from django.urls import path
from backend.handler.file import file, file_group

urlpatterns = (
    # 文件分组
    path('group/create', file_group.create),
    path('group/delete/<id>', file_group.delete),
    path('group/update', file_group.update),
    path('group/page', file_group.page),

    # 文件管理
    path('create', file.create),
    path('delete/<id>', file.delete),
    path('update', file.update),
    path('page', file.page),
)