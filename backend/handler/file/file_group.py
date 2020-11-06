from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from backend.exception.error_code import ErrorCode
from backend.util.utils import full_data
from backend.util.utils import get_params
from backend.util.utils import page_params
from backend.models import FileGroup
from backend.util.jwt_token import UserHolder
from backend.util.resp_data import Response
from backend.exception.exception import ValidateError, PlatformError


def create(request):
    """
    创建文件分组
    """
    body = full_data(request, 'POST')
    group = FileGroup(**body)
    try:
        group.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    group.save()
    return Response.success(group)


def delete(request, id):
    """
    根据 id 删除文件分组
    """
    full_data(request, 'DELETE')
    try:
        group = FileGroup.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    # 判断是否被文件使用
    group.delete()
    return Response.def_success()


def update(request):
    """
    修改文件分组
    """
    body = full_data(request, 'PUT')
    id, name = get_params(body, 'id', 'name')
    try:
        group = FileGroup.objects.get(owner=UserHolder.current_user(), id=id)
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
    分页查询文件分组
    """
    data = full_data(request, 'GET')
    page, page_size, name = page_params(data, 'name')
    groups = FileGroup.objects.filter(owner=UserHolder.current_user())
    if name:
        groups = groups.filter(name__contains=name)
    page_group = Paginator(groups, page_size)
    page_group.page(page)
    return Response.success(page_group)
