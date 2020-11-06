from django.urls import path
from backend.handler.contactor import contactor, contactor_group

urlpatterns = (
    # 联系人分组
    path('group/create', contactor_group.create),
    path('group/delete/<id>', contactor_group.delete),
    path('group/update', contactor_group.update),
    path('group/page', contactor_group.page),

    # 联系人
    path('create', contactor.create),
    path('delete', contactor.delete),
    path('update', contactor.update),
    path('page', contactor.page),
)