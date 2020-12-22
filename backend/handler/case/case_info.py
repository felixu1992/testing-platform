import random

from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from backend.exception import ErrorCode, PlatformError
from backend.handler import project
from backend.models import CaseInfo
from backend.util import UserHolder, Response, parse_data, page_params, get_params, update_fields, Executor, save


class CaseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseInfo
        fields = ['id', 'created_at', 'updated_at']


class CaseInfoViewSet(viewsets.ModelViewSet):
    queryset = CaseInfo

    serializer_class = CaseInfoSerializer

    def post(self, request):
        """
        新增用例
        """

        body = parse_data(request, 'POST')
        case_info = CaseInfo(**body)
        save(case_info)
        return Response.success(case_info)

    def delete(self, request, id):
        """
        根据 id 删除用例

        前端需要二次确认
        """

        parse_data(request, 'DELETE')
        case_info = get_by_id(id)
        case_info.delete()
        return Response.def_success()

    def put(self, request):
        """
        修改用例信息
        """

        data = parse_data(request, 'PUT')
        param_dict = get_params(data, 'id', 'name', 'remark', 'host', 'path', 'params', 'extend_keys', 'extend_values',
                                'headers', 'expected_http_status', 'check_status', 'run', 'developer', 'notify', 'sort')
        case_info = get_by_id(param_dict['id'])
        update_fields(case_info, **param_dict)
        save(case_info)
        return Response.success(case_info)

    @action(methods=['GET'], detail=False, url_path='page')
    def page(self, request):
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
                                                                                      'path',
                                                                                      'method', 'run',
                                                                                      'developer').values()
        if project_id is None:
            raise PlatformError.error_args(ErrorCode.MISSING_NECESSARY_KEY, 'project_id')
        case_infos = CaseInfo.objects.filter(owner=UserHolder.current_user(), project_id=project_id) \
            .contains(name=name, path=path).iexact(method=method).exact(run=run, developer=developer)
        page_case_infos = Paginator(case_infos, page_size)
        page_case_infos.page(page)
        return Response.success(case_infos)

    def get(self, request, id):
        """
        根据 id 查询用例详细信息
        """

        parse_data(request, 'GET')
        return Response.success(get_by_id(id))

    @action(methods=['POST'], detail=False, url_path='copy')
    def copy(self, request):
        """
        拷贝接口

        拷贝接口信息
        对于唯一属性，拷贝后添加随机数
        """

        data = parse_data(request, 'POST')
        old_case_info = get_by_id(get_params(data, 'id'))
        new_case_info = CaseInfo(old_case_info.__dict__.copy())
        new_case_info.id = None
        new_case_info.name = new_case_info.name + '_copy_' + str(random.randint(0, 99999))
        save(new_case_info)
        return Response.success(new_case_info)


    @action(methods=['GET'], detail=False, url_path='export')
    def export(self, request):
        """
        可以先不实现
        """

        print()

    @action(methods=['POST'], detail=False, url_path='execute')
    def execute(self, request):
        """
        执行项目下所有接口用例

        1. 执行接口用例
        2. 生成用例报告
        """

        data = parse_data(request, 'POST')
        case_info = get_by_id(get_params(data, 'id'))
        pro = project.get_by_id(case_info.project_id)
        executor = Executor(case_infos=[case_info], project=pro)
        reports = executor.execute()
        return Response.success(reports[0])


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