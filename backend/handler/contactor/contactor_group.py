from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from backend.exception.error_code import ErrorCode
from backend.handler.contactor import contactor
from backend.util.utils import full_data, page_params_dict, contains
from backend.util.utils import get_params
from backend.util.utils import page_params
from backend.models import ContactorGroup
from backend.util.jwt_token import UserHolder
from backend.util.resp_data import Response
from backend.exception.exception import ValidateError, PlatformError


def create(request):
    """
    创建联系人分组
    """

    body = full_data(request, 'POST')
    group = ContactorGroup(**body)
    try:
        group.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    group.save()
    return Response.success(group)


def delete(request, id):
    """
    根据 id 删除联系人分组
    """

    full_data(request, 'DELETE')
    group = get_by_id(id)
    # 判断是否被联系人使用
    count = contactor.count_by_group(id)
    if count > 0:
        raise PlatformError.error(ErrorCode.CONTACTOR_GROUP_HAS_CONTACTOR)
    group.delete()
    return Response.def_success()


def update(request):
    """
    修改联系人分组
    """

    body = full_data(request, 'PUT')
    id, name = get_params(body, 'id', 'name')
    group = get_by_id(id)
    if name:
        group.name = name
    try:
        group.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    group.save()
    return Response.success(group)


def page(request):
    """
    分页查询联系人分组

    可根据 name 做模糊
    """

    data = full_data(request, 'GET')
    page, page_size, name = page_params_dict(data, 'name').values()
    groups = ContactorGroup.objects.filter(owner=UserHolder.current_user())
    groups = contains(groups, name=name)
    page_group = Paginator(groups, page_size)
    page_group.page(page)
    return Response.success(page_group)


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    try:
        group = ContactorGroup.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    return group
