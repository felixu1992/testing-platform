from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator

from backend.exception import ErrorCode, ValidateError, PlatformError
from backend.handler.project import project
from backend.models import ProjectGroup
from backend.util import UserHolder, Response, full_data, get_params, page_params


def create(request):
    """
    创建项目分组
    """

    body = full_data(request, 'POST')
    group = ProjectGroup(**body)
    try:
        group.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    group.save()
    return Response.success(group)


def delete(request, id):
    """
    根据 id 删除项目分组
    """

    full_data(request, 'DELETE')
    group = get_by_id(id)
    # 是否被项目使用
    count = project.count_by_group(id)
    if count > 0:
        raise PlatformError.error(ErrorCode.PROJECT_GROUP_HAS_PROJECT)
    group.delete()
    return Response.def_success()


def update(request):
    """
    修改项目分组
    """

    body = full_data(request, 'PUT')
    id, name = get_params(body, 'id', 'name')
    group = get_by_id(id)
    group.name = name
    try:
        group.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    group.save()
    return Response.success(group)


def page(request):
    """
    分页查询项目分组

    可根据 name 模糊查询
    """

    data = full_data(request, 'GET')
    page, page_size, name = page_params(data, 'name')
    groups = ProjectGroup.objects.filter(owner=UserHolder.current_user())
    if name:
        groups = groups.filter(name__contains=name)
    page_group = Paginator(groups, page_size)
    page_group.page(page)
    return Response.success(page_group)


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询分组详情
    """

    try:
        group = ProjectGroup.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    return group
