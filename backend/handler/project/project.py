import random

from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from backend.exception import ErrorCode, ValidateError, PlatformError
from backend.handler.case import case_info
from backend.handler.project import project_group
from backend.handler.record import report, record
from backend.models import Project, CaseInfo
from backend.util import UserHolder, Response, parse_data, get_params, update_fields, page_params, Executor, save, \
    batch_save
from backend.settings import IGNORED, FAILED, PASSED


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'remark', 'headers', 'host', 'group_id', 'notify', 'created_at', 'updated_at']


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects

    serializer_class = ProjectSerializer

    def create(self, request, *args, **kwargs):
        """
        创建项目
        """

        body = parse_data(request, 'POST')
        project = Project(**body)
        # 校验分组是否存在
        project_group.get_by_id(project.group_id)
        save(project)
        return Response.success(project)

    def destroy(self, request, *args, **kwargs):
        """
        根据 id 删除项目

        前端需要二次确认，确认删除执行以下操作：
        1. 删除项目信息
        2. 删除关联接口用例信息
        3. 删除对应项目的历史报告(或者不删，让他有个后悔机会还能找回接口)
        """

        parse_data(request, 'DELETE')
        id = kwargs['pk']
        project = get_by_id(id)
        project.delete()
        # TODO 删用例和报告
        return Response.def_success()

    def update(self, request, *args, **kwargs):
        """
        修改项目信息
        """

        data = parse_data(request, 'PUT')
        params = get_params(data, 'id', 'name', 'remark', 'headers', 'host', toleration=True)
        project = get_by_id(params['id'])
        update_fields(project, **params)
        # 校验分组是否存在
        project_group.get_by_id(project.group_id)
        save(project)
        return Response.success(project)

    def list(self, request, *args, **kwargs):
        """
        分页查询项目

        可全量分页(当然只有自己的数据)
        可传入分组
        可传入 name 模糊
        """

        data = parse_data(request, 'GET')
        page, page_size, name, group_id = page_params(data, 'name', 'group_id').values()
        projects = Project.objects.filter(owner=UserHolder.current_user()).exact(group_id=group_id).contains(name=name)
        page_projects = Paginator(projects, page_size)
        result = page_projects.page(page)
        # 得到所有分组 id
        group_ids = [o.group_id for o in result.object_list]
        group_names = {}
        groups = project_group.get_list_by_ids(group_ids)
        for group in groups:
            group_names.update({group.id: group.name})
        for project in result.object_list:
            group_name = group_names[project.group_id]
            if group_name:
                project.group_name = group_name
        return Response.success(result)

    def retrieve(self, request, *args, **kwargs):
        """
        根据 id 查询项目详细信息
        """

        parse_data(request, 'GET')
        id = kwargs['pk']
        return Response.success(get_by_id(id))

    @action(methods=['POST'], detail=False, url_path='copy')
    def copy(self, request):
        """
        拷贝项目

        会拷贝以下内容：
        1. 项目信息
        2. 项目下接口信息
        """

        data = parse_data(request, 'POST')
        id, name = get_params(data, 'id', 'name').values()
        old_project = get_by_id(id)
        new_project = Project()
        new_project.__dict__ = old_project.__dict__.copy()
        new_project.id = None
        new_project.name = name
        save(new_project)
        case_infos = case_info.list_by_project(old_project.id)
        new_infos = []
        for info in case_infos:
            new_case_info = CaseInfo()
            new_case_info.__dict__ = info.__dict__.copy()
            new_case_info.id = None
            new_case_info.project_id = new_project.id
            new_infos.append(new_case_info)
        if new_infos:
            batch_save(CaseInfo.objects, new_infos)
        return Response.success(new_project)

    @action(methods=['POST'], detail=False, url_path='execute')
    def execute(self, request):
        """
        执行项目下所有接口用例

        1. 执行接口用例
        2. 生成用例报告
        """

        data = parse_data(request, 'POST')
        params = get_params(data, 'id')
        project = get_by_id(params['id'])
        case_infos = case_info.list_by_project(project.id)
        if not case_infos:
            raise PlatformError.error(ErrorCode.PROJECT_NOT_HAVE_CASES)
        executor = Executor(case_infos=case_infos, project=project)
        reports = executor.execute()
        # 构建记录
        ignored_num = [obj for obj in reports if getattr(obj, 'status') == IGNORED]
        passed_num = [obj for obj in reports if getattr(obj, 'status') == PASSED]
        failed_num = [obj for obj in reports if getattr(obj, 'status') == FAILED]
        reco = record.create(group_id=project.group_id, project_id=project.id, owner=project.owner,
                             total=len(case_infos), ignored=len(ignored_num), passed=len(passed_num),
                             failed=len(failed_num))
        for result in reports:
            result.record_id = reco.id
            report.create(result)
        return Response.success(reco)


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询项目
    """

    try:
        project = Project.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error_args(ErrorCode.DATA_NOT_EXISTED, '项目', 'id')
    return project


def get_list_by_ids(ids):
    """
    根据 id 数组查询
    """

    return Project.objects.owner().fields_in(id=ids)


def count_by_group(group_id):
    """
    统计指定 group id 下项目数
    """

    return Project.objects.filter(owner=UserHolder.current_user(), group_id=group_id).count()
