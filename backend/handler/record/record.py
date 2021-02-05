from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from backend.exception import ErrorCode, PlatformError
from backend.models import Record, Report
from backend.handler.project import project, project_group
from backend.util import UserHolder, Response, parse_data, page_params, save


class RecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = Record
        fields = ['id', 'group_id', 'project_id', 'remark', 'passed', 'failed', 'ignored', 'total', 'created_at',
                  'updated_at']


class RecordViewSet(viewsets.ModelViewSet):
    queryset = Record

    serializer_class = RecordSerializer

    def destroy(self, request, *args, **kwargs):
        """
        根据 id 删除记录

        前端需要二次确认，确认删除执行以下操作：
        1. 删除记录
        2. 删除所属用例结果
        """

        parse_data(request, 'DELETE')
        id = kwargs['pk']
        record = get_by_id(id)
        record.delete()
        # 删除用例执行结果
        Report.objects.owner().filter(record_id=id).delete()
        return Response.def_success()

    def list(self, request, *args, **kwargs):
        """
        分页查询记录

        可全量分页(当然只有自己的数据)
        可传入项目分组
        可传入项目
        """

        data = parse_data(request, 'GET')
        page, page_size, name, group_id, project_name = page_params(data, 'name', 'group_id', 'project_name').values()
        records = Record.objects.filter(owner=UserHolder.current_user()).exact(group_id=group_id)
        page_projects = Paginator(records, page_size)
        result = page_projects.page(page)
        group_ids = [o.group_id for o in result.object_list]
        groups = project_group.get_list_by_ids(group_ids)
        group_names = {o.id: o.name for o in groups}
        project_ids = [o.project_id for o in result.object_list]
        projects = project.get_list_by_ids(project_ids)
        project_names = {o.id: o.name for o in projects}
        for record in result.object_list:
            record.group_name = group_names[record.group_id]
            record.project_name = project_names[record.project_id]
        return Response.success(result)

    @action(methods=['GET'], detail=False, url_path='export')
    def export(self, request, id):
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
        raise PlatformError.error_args(ErrorCode.DATA_NOT_EXISTED, '测试记录', 'id')
    return record


def count():
    """
    查询记录总数
    """

    return Record.objects.owner().count()


def create(**kwargs):
    """
    创建测试记录
    """

    record = Record(**kwargs)
    save(record)
    return record
