from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from backend.exception.error_code import ErrorCode
from backend.util.utils import full_data
from backend.util.utils import get_params
from backend.util.utils import page_params
from backend.models import Contactor
from backend.util.jwt_token import UserHolder
from backend.util.resp_data import Response
from backend.exception.exception import ValidateError, PlatformError


def create(request):
    """
    创建联系人
    """
    body = full_data(request, 'POST')
    contactor = Contactor(**body)
    try:
        contactor.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    contactor.save()
    return Response.success(contactor)


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
        contactors = contactors.filter(name__contains=name)
    if phone:
        contactors = contactors.filter(phone__contains=phone)
    if email:
        contactors = contactors.filter(email__contains=email)
    page_contactors = Paginator(contactors, page_size)
    page_contactors.page(page)
    return Response.success(page_contactors)

