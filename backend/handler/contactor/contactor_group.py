from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from backend.exception import ErrorCode, ValidateError, PlatformError
from backend.handler import contactor
from backend.models import ContactorGroup
from backend.util import UserHolder, Response, get_params_dict, full_data, page_params_dict, update_fields


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
    id, name = get_params_dict(body, 'id', 'name').values()
    group = get_by_id(id)
    update_fields(group, name=name)
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
    groups = ContactorGroup.objects.filter(owner=UserHolder.current_user()).contains(name=name)
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
