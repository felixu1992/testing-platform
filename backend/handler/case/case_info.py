from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator

from backend.exception.error_code import ErrorCode
from backend.exception.exception import ValidateError, PlatformError
from backend.models import CaseInfo
from backend.util.jwt_token import UserHolder
from backend.util.resp_data import Response
from backend.util.utils import full_data, get_params, page_params


def create(request):
    """
    新增用例
    """

    body = full_data(request, 'POST')
    case_info = CaseInfo(**body)
    try:
        case_info.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    case_info.save()
    return Response.success(case_info)


def delete(request, id):
    """
    根据 id 删除项目

    前端需要二次确认
    """

    full_data(request, 'DELETE')
    project = get_by_id(id)
    project.delete()
    return Response.def_success()


def update(request):
    """
    修改项目信息
    """

    # id = models.AutoField(primary_key=True)
    # name = models.CharField(verbose_name='用例名称', max_length=32, unique=True,
    #                         validators=[MinLengthValidator(1, message='最小长度为 1'),
    #                                     MaxLengthValidator(32, message='最大长度为 32')])
    # remark = models.CharField(verbose_name='项目备注', max_length=255, blank=True, null=True,
    #                           validators=[MinLengthValidator(1, message='最小长度为 1'),
    #                                       MaxLengthValidator(255, message='最大长度为 255')])
    # method = models.CharField(verbose_name='请求方法', max_length=8,
    #                           validators=[MinLengthValidator(1, message='最小长度为 1'),
    #                                       MaxLengthValidator(8, message='最大长度为 8')])
    # host = models.CharField(verbose_name='请求 host，没填会使用项目的', max_length=255, blank=True, null=True)
    # path = models.CharField(verbose_name='请求地址', max_length=255,
    #                         validators=[MinLengthValidator(1, message='最小长度为 1'),
    #                                     MaxLengthValidator(255, message='最大长度为 255')])
    # params = models.JSONField(verbose_name='请求参数', blank=True, null=True)
    # extend_keys = models.TextField(verbose_name='扩展字段', blank=True, null=True)
    # extend_values = models.TextField(verbose_name='扩展值', blank=True, null=True)
    # headers = models.JSONField(verbose_name='请求头', blank=True, null=True)
    # expected_keys = models.TextField(verbose_name='预期字段', blank=True, null=True)
    # expected_values = models.TextField(verbose_name='预期值', blank=True, null=True)
    # check_step = models.TextField(verbose_name='校验步骤', blank=True, null=True)
    # expected_http_status = models.IntegerField(verbose_name='Http 状态码', default=200,
    #                                            validators=[MinValueValidator(1, message='最小值为 1')])
    # check_status = models.BooleanField(verbose_name='是否校验 Http 状态', default=False)
    # run = models.BooleanField(verbose_name='是否运行', default=True)
    # owner = models.IntegerField(verbose_name='拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    # developer = models.IntegerField(verbose_name='接口开发者', default=0,
    #                                 validators=[MinValueValidator(1, message='最小值为 1')])
    # notify = models.BooleanField(verbose_name='是否通知开发者', default=False)
    # project_id = models.IntegerField(verbose_name='关联项目 id', validators=[MinValueValidator(1, message='最小值为 1')])
    # sort = models.IntegerField(verbose_name='接口排序', default=0, validators=[MinValueValidator(1, message='最小值为 1')])
    data = full_data(request, 'PUT')
    id, name, remark, cookies, headers, host = get_params(data, 'id', 'name', 'remark', 'host', 'path', 'params',
                                                          'extend_keys', 'extend_values', 'headers',
                                                          'expected_http_status', 'check_status', 'run')
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
    必须传入项目 id
    可传入 name 模糊
    可传入 path 模糊
    可传入 method 精确匹配
    可传入 run 精确匹配
    可传入 developer 精确匹配
    """

    data = full_data(request, 'GET')
    page, page_size, project_id, name, path, method, run, developer = page_params(data, 'project_id', 'name', 'path',
                                                                                  'method', 'run', 'developer')
    if project_id is None:
        raise PlatformError.error_args(ErrorCode.MISSING_NECESSARY_KEY, 'project_id')
    case_infos = CaseInfo.objects.filter(owner=UserHolder.current_user(), project_id=project_id)
    if name:
        case_infos = case_infos.filter(name__contains=name)
    if path:
        case_infos = case_infos.filter(path__contains=path)
    if method:
        case_infos = case_infos.filter(method__iexact=method)
    if run:
        case_infos = case_infos.filter(run__exact=run)
    if developer:
        case_infos = case_infos.filter(developer__exact=developer)
    page_case_infos = Paginator(case_infos, page_size)
    page_case_infos.page(page)
    return Response.success(case_infos)


def detail(request, id):
    """
    根据 id 查询用例详细信息
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


def export(request):
    """
    可以先不实现
    """

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
        case_info = CaseInfo.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    return case_info


def list_by_project(project_id):
    """
    根据项目分页查询接口列表
    """

    return CaseInfo.objects.filter(owner=UserHolder.current_user(), project_id=project_id)
