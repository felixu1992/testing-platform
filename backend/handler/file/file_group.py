from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework import serializers, viewsets
from rest_framework.decorators import action

from backend.exception import ErrorCode, ValidateError, PlatformError
from backend.handler import file
from backend.models import FileGroup
from backend.util import Response, parse_data, get_params, update_fields, page_params


class FileGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = FileGroup
        fields = ['id', 'name', 'created_at', 'updated_at']


class FileGroupViewSet(viewsets.ModelViewSet):

    queryset = FileGroup

    serializer_class = FileGroupSerializer

    def post(self, request):
        """
        创建文件分组
        """

        body = parse_data(request, 'POST')
        group = FileGroup(**body)
        try:
            group.full_clean()
        except ValidationError as e:
            raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
        group.save()
        return Response.success(group)

    def delete(self, request, id):
        """
        根据 id 删除文件分组
        """

        parse_data(request, 'DELETE')
        group = get_by_id(id)
        # 判断是否被文件使用
        count = file.count_by_group(id)
        if count > 0:
            raise PlatformError.error(ErrorCode.FILE_GROUP_HAS_FILE)
        group.delete()
        return Response.def_success()

    def put(self, request):
        """
        修改文件分组
        """

        body = parse_data(request, 'PUT')
        id, name = get_params(body, 'id', 'name').values()
        group = get_by_id(id)
        update_fields(group, name=name)
        try:
            group.full_clean()
        except ValidationError as e:
            raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
        group.save()
        return Response.success(group)

    @action(methods=['GET'], detail=False, url_path='page')
    def page(self, request):
        """
        分页查询文件分组

        可根据 name 模糊查询
        """

        data = parse_data(request, 'GET')
        page, page_size, name = page_params(data, 'name').values()
        groups = FileGroup.objects.owner().contains(name=name)
        page_group = Paginator(groups, page_size)
        page_group.page(page)
        return Response.success(page_group)


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询文件分组
    """

    try:
        group = FileGroup.objects.owner().get(id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    return group
