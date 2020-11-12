from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator

from backend.exception import ErrorCode, PlatformError
from backend.models import Record
from backend.util import UserHolder, Response, parse_data, page_params


def delete(request, id):
    """
    根据 id 删除记录

    前端需要二次确认，确认删除执行以下操作：
    1. 删除记录
    2. 删除所属用例结果
    """

    parse_data(request, 'DELETE')
    record = get_by_id(id)
    record.delete()
    # TODO 删用例结果
    return Response.def_success()


def page(request):
    """
    分页查询记录

    可全量分页(当然只有自己的数据)
    可传入项目分组
    可传入项目
    """

    data = parse_data(request, 'GET')
    page, page_size, group_id, project_id = page_params(data, 'name', 'group_id').values()
    records = Record.objects.filter(owner=UserHolder.current_user()).exact(group_id=group_id).exact(project_id=project_id)
    page_projects = Paginator(records, page_size)
    page_projects.page(page)
    return Response.success(records)


def export(request, id):
    # TODO 导出 Excel
    print()


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询记录
    """

    try:
        record = Record.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    return record
