from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from backend.exception.error_code import ErrorCode
from backend.util.utils import full_data
from backend.util.utils import get_params
from backend.util.utils import page_params
from backend.models import ContactorGroup
from backend.util.jwt_token import UserHolder
from backend.util.resp_data import Response
from backend.exception.exception import ValidateError, PlatformError


def test(request):
    body = full_data(request, 'POST')
    print(request)
    return Response.def_success()


def create(request):
    """
    创建联系人分组
    """
    body = full_data(request, 'POST')
    group = ContactorGroup(**body)
    group.owner = UserHolder.current_user()
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
    params = full_data(request, 'DELETE')
    id = get_params(params, 'id')
    try:
        group = ContactorGroup.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    group.delete()
    return Response.def_success()


def update(request):
    """
    修改联系人分组
    """
    body = full_data(request, 'PUT')
    id, name = get_params(body, 'id', 'name')
    try:
        group = ContactorGroup.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
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
    """
    data = full_data(request, 'GET')
    page, page_size, name = page_params(data, 'name')
    groups = ContactorGroup.objects.filter(owner=UserHolder.current_user())
    if name:
        groups = groups.filter(name__contains=name)
    page_group = Paginator(groups, page_size)
    page_group.page(page)
    return Response.success(page_group)
