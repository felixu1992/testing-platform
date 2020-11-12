from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from backend.exception import ErrorCode, ValidateError, PlatformError
from backend.models import Report
from backend.util import UserHolder, Response, parse_data, get_params, update_fields, page_params


def page(request):
    """
    分页查询项目

    可全量分页(当然只有自己的数据)
    可传入分组
    可传入 name 模糊
    """

    data = parse_data(request, 'GET')
    page, page_size, name, group_id = page_params(data, 'name', 'group_id').values()
    projects = Report.objects.filter(owner=UserHolder.current_user()).exact(group_id=group_id).contains(name=name)
    page_projects = Paginator(projects, page_size)
    page_projects.page(page)
    return Response.success(projects)


def detail(request, id):
    """
    根据 id 查询项目详细信息
    """

    parse_data(request, 'GET')
    return Response.success(get_by_id(id))


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询项目
    """

    try:
        report = Report.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    return report
