from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.paginator import Paginator
from rest_framework import serializers, viewsets
from rest_framework.decorators import action

from backend.exception import ErrorCode, PlatformError, ValidateError
from backend.models import Record
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
        # TODO 删用例结果
        return Response.def_success()

    def list(self, request, *args, **kwargs):
        """
        分页查询记录

        可全量分页(当然只有自己的数据)
        可传入项目分组
        可传入项目
        """

        data = parse_data(request, 'GET')
        page, page_size, group_id, project_id = page_params(data, 'name', 'group_id').values()
        records = Record.objects.filter(owner=UserHolder.current_user()).exact(group_id=group_id).exact(
            project_id=project_id)
        page_projects = Paginator(records, page_size)
        result = page_projects.page(page)
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


def create(**kwargs):
    """
    创建测试记录
    """

    record = Record(**kwargs)
    save(record)
    return record
