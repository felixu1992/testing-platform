from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from backend.exception import ErrorCode, ValidateError, PlatformError
from backend.models import Project
from backend.util import UserHolder, Response, full_data, get_params, page_params


def create(request):
    """
    创建项目
    """

    body = full_data(request, 'POST')
    project = Project(**body)
    try:
        project.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    project.save()
    return Response.success(project)


def delete(request, id):
    """
    根据 id 删除项目

    前端需要二次确认，确认删除执行以下操作：
    1. 删除项目信息
    2. 删除关联接口用例信息
    3. 删除对应项目的历史报告(或者不删，让他有个后悔机会还能找回接口)
    """

    full_data(request, 'DELETE')
    project = get_by_id(id)
    project.delete()
    # TODO 删用例和报告
    return Response.def_success()


def update(request):
    """
    修改项目信息
    """

    data = full_data(request, 'PUT')
    id, name, remark, cookies, headers, host = get_params(data, 'id', 'name', 'remark', 'cookies', 'headers', 'host',
                                                          toleration=True)
    project = get_by_id(id)
    if name:
        project.name = name
    if remark:
        project.remark = remark
    if cookies:
        project.cookies = cookies
    if headers:
        project.headers = headers
    if host:
        project.host = host
    try:
        project.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    project.save()
    return Response.success(project)


def page(request):
    """
    分页查询项目

    可全量分页(当然只有自己的数据)
    可传入分组
    可传入 name 模糊
    """

    data = full_data(request, 'GET')
    page, page_size, name, group_id = page_params(data, 'name', 'group_id')
    projects = Project.objects.filter(owner=UserHolder.current_user())
    if name:
        projects = projects.filter(name__contains=name)
    if group_id:
        projects = projects.filter(group_id=group_id)
    page_projects = Paginator(projects, page_size)
    page_projects.page(page)
    return Response.success(projects)


def detail(request, id):
    """
    根据 id 查询项目详细信息
    """

    full_data(request, 'GET')
    return Response.success(get_by_id(id))


def copy(request):
    """
    该实现用来拷贝项目

    会拷贝以下内容：
    1. 项目信息
    2. 项目下接口信息
    """

    # TODO copy
    print()


def execute(request):
    """
    执行项目下所有接口用例

    1. 执行接口用例
    2. 生成用例报告
    """

    print()


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询项目
    """

    try:
        project = Project.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    return project


def count_by_group(group_id):
    """
    统计指定 group id 下项目数
    """

    return Project.objects.filter(owner=UserHolder.current_user(), group_id=group_id).count()
