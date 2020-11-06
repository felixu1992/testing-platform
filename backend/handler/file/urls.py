from django.urls import path
from backend.handler.file import file, file_group

urlpatterns = (
    # 联系人分组
    path('group/create', file_group.create),
    path('group/delete/<id>', file_group.delete),
    path('group/update', file_group.update),
    path('group/page', file_group.page),

    # 联系人
    path('create', file.create),
    path('delete', file.delete),
    path('update', file.update),
    path('page', file.page),
)