from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework import serializers, viewsets
from rest_framework.decorators import action

from backend.exception import ErrorCode, ValidateError, PlatformError
from backend.handler import file
from backend.models import FileGroup
from backend.util import Response, parse_data, get_params, update_fields, page_params, save


class FileGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileGroup
        fields = ['id', 'name', 'created_at', 'updated_at']


class FileGroupViewSet(viewsets.ModelViewSet):
    queryset = FileGroup.objects

    serializer_class = FileGroupSerializer

    def create(self, request, *args, **kwargs):
        """
        创建文件分组
        """

        body = parse_data(request, 'POST')
        group = FileGroup(**body)
        save(group)
        return Response.success(group)

    def destroy(self, request, *args, **kwargs):
        """
        根据 id 删除文件分组
        """

        parse_data(request, 'DELETE')
        id = kwargs['pk']
        group = get_by_id(id)
        # 判断是否被文件使用
        try:
            from backend.handler.file.file import count_by_group
        except ImportError:
            raise PlatformError.error(ErrorCode.FAIL)
        count = count_by_group(id)
        if count > 0:
            raise PlatformError.error(ErrorCode.FILE_GROUP_HAS_FILE)
        group.delete()
        return Response.def_success()

    def update(self, request, *args, **kwargs):
        """
        修改文件分组
        """

        body = parse_data(request, 'PUT')
        id, name = get_params(body, 'id', 'name').values()
        group = get_by_id(id)
        update_fields(group, name=name)
        save(group)
        return Response.success(group)

    def list(self, request, *args, **kwargs):
        """
        分页查询文件分组

        可根据 name 模糊查询
        """

        data = parse_data(request, 'GET')
        page, page_size, name = page_params(data, 'name').values()
        groups = FileGroup.objects.owner().contains(name=name)
        page_group = Paginator(groups, page_size)
        result = page_group.page(page)
        return Response.success(result)


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询文件分组
    """

    try:
        group = FileGroup.objects.owner().get(id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error_args(ErrorCode.DATA_NOT_EXISTED, '文件分组', 'id')
    return group


def get_list_by_ids(ids):
    """
    根据 id 数组查询
    """

    return FileGroup.objects.owner().fields_in(id=ids)
