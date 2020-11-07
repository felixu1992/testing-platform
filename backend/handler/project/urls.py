from django.urls import path
from backend.handler.project import project_group

urlpatterns = (
    # 文件分组
    path('group/create', project_group.create),
    path('group/delete/<id>', project_group.delete),
    path('group/update', project_group.update),
    path('group/page', project_group.page),

    # 文件管理
    # path('create', file.create),
    # path('delete/<id>', file.delete),
    # path('update', file.update),
    # path('page', file.page),
    # path('download/<id>', file.download)
)