import os
import time
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import FileResponse
from django.utils.http import urlquote
from backend.exception.error_code import ErrorCode
from backend.util.utils import full_data
from backend.util.utils import get_params
from backend.util.utils import page_params
from backend.models import File
from backend.util.jwt_token import UserHolder
from backend.util.resp_data import Response
from backend.exception.exception import ValidateError, PlatformError
from testing_platform.settings import FILE_REPO


def create(request):
    """
    创建文件
    """
    print(os.path.dirname(os.path.abspath(__file__)))
    body = full_data(request, 'POST')
    file = File(**body)
    # 处理文件
    file.path = __file_data(request)
    try:
        file.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    file.save()
    return Response.success(file)


def __file_data(request):
    # 获得所有文件
    files = request.FILES.getlist('files')
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


def download(request):
    print('-------------')
    # file = open(file_info.file_path, 'rb')
    # response = FileResponse(file)
    # response['Content-Disposition'] = 'attachment;filename="%s"' % urlquote(file_info.file_name)
    # return response


def delete(request, id):
    """
    根据 id 删除联系人
    """
    full_data(request, 'DELETE')
    try:
        contactor = Contactor.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    # TODO 判断是否被用例使用
    contactor.delete()
    return Response.def_success()


def update(request):
    """
    修改联系人
    """
    data = full_data(request, 'PUT')
    id, name = get_params(data, 'id', 'name')
    try:
        contractor = Contactor.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    contractor.name = name
    try:
        contractor.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    contractor.save()
    return Response.success(contractor)


def page(request):
    """
    分页查询联系人
    可全量分页(当然只有自己的数据)
    可传入分组
    可传入 name 模糊
    可传入 phone 模糊
    可传入 email 模糊
    """
    data = full_data(request, 'GET')
    page, page_size, name, phone, email = page_params(data, 'name', 'phone', 'email')
    contactors = Contactor.objects.filter(owner=UserHolder.current_user())
    if name:
        contactors = contactors.filer(name__contains=name)
    if phone:
        contactors = contactors.filer(phone__contains=phone)
    if email:
        contactors = contactors.filer(email__contains=email)
    page_contactors = Paginator(contactors, page_size)
    page_contactors.page(page)
    return Response.success(page_contactors)
