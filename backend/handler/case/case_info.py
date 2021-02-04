import json
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.db import transaction
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from backend.exception import ErrorCode, PlatformError
from backend.handler.contactor import contactor
from backend.handler.project import project
from backend.models import CaseInfo
from backend.util import UserHolder, Response, parse_data, page_params, get_params, update_fields, Executor, save, \
    batch_update

fields_cache = ['id', 'name', 'remark', 'method', 'host', 'path', 'params', 'extend_keys', 'extend_values',
                'headers', 'expected_keys', 'expected_values', 'expected_http_status', 'check_status', 'run',
                'developer', 'sort', 'delay', 'sample']


class CaseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseInfo
        copy = fields_cache.copy()
        copy.append('created_at')
        copy.append('updated_at')
        fields = copy


class CaseInfoViewSet(viewsets.ModelViewSet):
    queryset = CaseInfo.objects

    serializer_class = CaseInfoSerializer

    def create(self, request, *args, **kwargs):
        """
        新增用例
        """

        body = parse_data(request, 'POST')
        case_info = CaseInfo(**body)
        # 获取最大的 sort 值
        max_sort = CaseInfo.objects.owner().order_by('-sort').values('sort').first()
        case_info.sort = int(max_sort['sort']) + 1
        # 参数校验
        check_params(case_info)
        encoding(case_info)
        save(case_info)
        return Response.success(case_info)

    def destroy(self, request, *args, **kwargs):
        """
        根据 id 删除用例

        前端需要二次确认
        """

        parse_data(request, 'DELETE')
        id = kwargs['pk']
        case_info = get_by_id(id)
        case_info.delete()
        return Response.def_success()

    def update(self, request, *args, **kwargs):
        """
        修改用例信息
        """

        data = parse_data(request, 'PUT')
        param_dict = get_params(data, *fields_cache)
        case_info = get_by_id(param_dict['id'])
        update_fields(case_info, **param_dict)
        # 参数校验
        check_params(case_info)
        encoding(case_info)
        save(case_info)
        return Response.success(case_info)

    def list(self, request, *args, **kwargs):
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

        data = parse_data(request, 'GET')
        page, page_size, project_id, name, path, method, run, developer = page_params(data, 'project_id', 'name',
                                                                                      'path', 'method', 'run',
                                                                                      'developer').values()
        if project_id is None:
            raise PlatformError.error_args(ErrorCode.MISSING_NECESSARY_KEY, 'project_id')
        pro = project.get_by_id(project_id)
        case_infos = CaseInfo.objects.owner().exact(project_id=project_id).contains(name=name, path=path).iexact(
            method=method).exact(run=run, developer=developer)
        page_case_infos = Paginator(case_infos, page_size)
        result = page_case_infos.page(page)
        # 得到所有开发者 id
        developer_ids = [o.developer for o in result.object_list if o.developer]
        developer_names = {}
        developers = contactor.get_list_by_ids(developer_ids)
        for developer in developers:
            developer_names.update({developer.id: developer.name})
        for case_info in result.object_list:
            if case_info.developer:
                case_info.developer_name = developer_names[case_info.developer]
            case_info.project_name = pro.name
            decoding(case_info)
        return Response.success(result)

    def retrieve(self, request, *args, **kwargs):
        """
        根据 id 查询用例详细信息
        """

        parse_data(request, 'GET')
        case_info = get_by_id(kwargs['pk'])
        decoding(case_info)
        return Response.success(case_info)

    @action(methods=['POST'], detail=False, url_path='copy')
    def copy(self, request):
        """
        拷贝接口

        拷贝接口信息
        对于唯一属性，拷贝后添加随机数
        """

        data = parse_data(request, 'POST')
        id, name = get_params(data, 'id', 'name').values()
        old_case_info = get_by_id(id)
        new_case_info = CaseInfo()
        new_case_info.__dict__ = old_case_info.__dict__.copy()
        new_case_info.id = None
        new_case_info.name = name
        # 获取最大的 sort 值
        max_sort = CaseInfo.objects.owner().order_by('-sort').values('sort').first()
        new_case_info.sort = int(max_sort['sort']) + 1
        save(new_case_info)
        return Response.success(new_case_info)

    @action(methods=['GET'], detail=False, url_path='export')
    def export(self, request):
        """
        可以先不实现
        """

        pass

    @action(methods=['POST'], detail=False, url_path='import')
    def imported(self, request):
        """
        用例 Excel 的导入
        """

        pass

    @action(methods=['POST'], detail=False, url_path='compatible')
    def compatible(self, request):
        """
        临时接口，对前一版本的用例 Excel 进行兼容
        """

        pass

    @action(methods=['POST'], detail=False, url_path='execute')
    def execute(self, request):
        """
        执行项目下所有接口用例

        1. 执行接口用例
        2. 生成用例报告
        """

        data = parse_data(request, 'POST')
        params = get_params(data, 'id')
        case_info = get_by_id(params['id'])
        pro = project.get_by_id(case_info.project_id)
        executor = Executor(case_infos=[case_info], project=pro)
        reports = executor.execute()
        result = {}
        properties = reports[0].__dict__
        for k, v in properties.items():
            if k in result.keys() or k.startswith('_'):
                continue
            if k == 'owner':
                continue
            result[k] = v
        return Response.success(result)

    @action(methods=['PUT'], detail=False, url_path='sort')
    def sort(self, request):
        data = parse_data(request, 'PUT')
        source, transfer = get_params(data, 'source', 'transfer').values()
        get_by_sort(source)
        target = None
        if transfer == 'drag':
            target = get_params(data, 'target')['target']
            get_by_sort(target)
        if transfer == 'up':
            tar = CaseInfo.objects.owner().lt(source).last()
            if tar is None:
                return Response.def_success()
            target = tar.sort
        if transfer == 'down':
            tar = CaseInfo.objects.owner().gt(source).first()
            if tar is None:
                return Response.def_success()
            target = tar.sort
        if transfer == 'top':
            tar = CaseInfo.objects.owner().first()
            if tar is None:
                return Response.def_success()
            target = tar.sort
        if target is None:
            return Response.def_success()
        # 是否上移
        if source == target:
            return Response.def_success()
        deal_sort(source, target)
        return Response.def_success()


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------
@transaction.atomic
def deal_sort(source, target):
    up = source > target
    if up:
        min_sort = int(target)
        max_sort = int(source)
    else:
        min_sort = int(source)
        max_sort = int(target)
    # 介于之间的数据
    case_infos = CaseInfo.objects.owner().gt(e=True, sort=min_sort).lt(e=True, sort=max_sort)
    flag = True
    _source = None
    case_infos = sorted(case_infos, key=lambda o: o.sort, reverse=up) if up else case_infos
    for case in case_infos:
        if case.sort == source:
            case.sort = target
        else:
            if up:
                case.sort += 1
            else:
                case.sort -= 1
    batch_update(CaseInfo.objects, case_infos, ['sort'])


def check_params(case_info):
    """
    对用例的参数进行校验

    校验开发者是否存在
    校验项目是否存在
    校验预期字段和预期值列表是否匹配
    校验注入字段和注入值列表是否匹配
    """

    # 开发者
    if case_info.developer:
        contactor.get_by_id(case_info.developer)
    # 项目
    project.get_by_id(case_info.project_id)
    # 预期
    if (case_info.expected_keys is None and case_info.expected_values) or (
            case_info.expected_keys and case_info.expected_values is None) or (
            (case_info.expected_keys and case_info.expected_values) and len(case_info.expected_keys) != len(
        case_info.expected_values)):
        raise PlatformError.error(ErrorCode.EXPECTED_NOT_ALLOWED)
    if (case_info.extend_keys is None and case_info.extend_values) or (
            case_info.extend_keys and case_info.extend_values is None) or (
            (case_info.extend_keys and case_info.extend_values) and len(case_info.extend_keys) != len(
        case_info.extend_values)):
        raise PlatformError.error(ErrorCode.DEPEND_NOT_ALLOWED)
    # TODO 对注入参数、预期值等的数据格式做校验


def get_by_sort(sort):
    """
    根据 sort 查询用例
    """
    try:
        case_info = CaseInfo.objects.get(owner=UserHolder.current_user(), sort=sort)
    except ObjectDoesNotExist:
        raise PlatformError.error_args(ErrorCode.DATA_NOT_EXISTED, '用例', 'sort')
    return case_info


def get_by_id(id):
    """
    根据 id 查询用例
    """

    try:
        case_info = CaseInfo.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error_args(ErrorCode.DATA_NOT_EXISTED, '用例', 'id')
    return case_info


def count():
    """
    查询用例总数
    """

    return CaseInfo.objects.owner().count()


def list_by_project(project_id):
    """
    根据项目分页查询接口列表
    """

    return CaseInfo.objects.filter(owner=UserHolder.current_user(), project_id=project_id)


def encoding(case_info):
    """
    对部分参数进行编码操作
    """

    if case_info.extend_keys:
        case_info.extend_keys = json.dumps(case_info.extend_keys)
    if case_info.extend_values:
        case_info.extend_values = json.dumps(case_info.extend_values)
    if case_info.expected_keys:
        case_info.expected_keys = json.dumps(case_info.expected_keys)
    if case_info.expected_values:
        case_info.expected_values = json.dumps(case_info.expected_values)


def decoding(case_info):
    """
    对部分参数进行解码操作
    """

    if case_info.extend_keys:
        case_info.extend_keys = json.loads(case_info.extend_keys)
    if case_info.extend_values:
        case_info.extend_values = json.loads(case_info.extend_values)
    if case_info.expected_keys:
        case_info.expected_keys = json.loads(case_info.expected_keys)
    if case_info.expected_values:
        case_info.expected_values = json.loads(case_info.expected_values)


# -------------------------------------------- 临时 -----------------------------------------
def create_case(case):
    # 获取最大的 sort 值
    max_sort = CaseInfo.objects.owner().order_by('-sort').values('sort').first()
    case.sort = int(max_sort['sort']) + 1
    # 参数校验
    check_params(case)
    encoding(case)
    save(case)
