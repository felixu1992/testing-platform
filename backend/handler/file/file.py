import os
import time
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import FileResponse
from django.utils.http import urlquote
from backend.exception import ErrorCode, ValidateError, PlatformError
from backend.models import File
from backend.util import UserHolder, Response, parse_data, get_params, update_fields, page_params
from backend import FILE_REPO


def create(request):
    """
    创建文件
    """
    body = parse_data(request, 'POST')
    file = File(**body)
    # 处理文件
    file.path = __file_data(request)
    try:
        file.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    file.save()
    return Response.success(file)


def delete(request, id):
    """
    根据 id 删除文件
    """
    parse_data(request, 'DELETE')
    file = get_by_id(id)
    # TODO 判断是否被用例使用
    file.delete()
    return Response.def_success()


def update(request):
    """
    修改联系人
    """
    data = parse_data(request, 'PUT')
    id, name, remark = get_params(data, 'id', 'name', 'remark', toleration=True).values()
    file = get_by_id(id)
    # 处理文件
    path = __file_data(request)
    update_fields(file, name=name, remark=remark, path=path)
    try:
        file.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    file.save()
    return Response.success(file)


def page(request):
    """
    分页查询文件列表
    可全量分页(当然只有自己的数据)
    可传入分组
    可传入 name 模糊
    """
    data = parse_data(request, 'GET')
    page, page_size, name = page_params(data, 'name').values()
    files = File.objects.filter(owner=UserHolder.current_user()).contains(name=name)
    page_files = Paginator(files, page_size)
    page_files.page(page)
    return Response.success(page_files)


def download(request, id):
    parse_data(request, 'GET')
    file = get_by_id(id)
    path = file.path
    file = open(path, 'rb')
    response = FileResponse(file)
    ps = path.split('.')
    suffix = ps[len(ps) - 1]
    response['Content-Disposition'] = 'attachment;filename="%s"' % urlquote(file.name + '.' + suffix)
    return response


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询文件信息
    """

    try:
        file = File.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    return file


def count_by_group(group_id):
    """
    根据分组 id 计数
    """

    return File.objects.filter(owner=UserHolder.current_user(), group_id=group_id).count()


def __file_data(request, toleration=False):
    # 获得所有文件
    files = request.FILES.getlist('files')
    if toleration and len(files) == 0:
        return None
    if len(files) == 0 or len(files) > 1:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, '请检查文件数目，需要有且仅有一个文件')
    file = files[0]
    file_path = os.path.join(FILE_REPO, str(int(time.time() * 1000)) + file.name)
    # 写文件
    dest = open(file_path, 'wb+')
    for chunk in file.chunks():
        dest.write(chunk)
    dest.close()
    # 返回文件路径
    return file_path
