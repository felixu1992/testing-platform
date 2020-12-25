from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework import serializers, viewsets
from backend.exception import ErrorCode, PlatformError
from backend.models import ProjectGroup
from backend.util import Response, parse_data, get_params, update_fields, page_params, save


class ProjectGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectGroup
        fields = ['id', 'name', 'created_at', 'updated_at']


class ProjectGroupViewSet(viewsets.ModelViewSet):
    queryset = ProjectGroup.objects

    serializer_class = ProjectGroupSerializer

    def create(self, request, *args, **kwargs):
        """
        创建项目分组
        """

        body = parse_data(request, 'POST')
        group = ProjectGroup(**body)
        save(group)
        return Response.success(group)

    def destroy(self, request, *args, **kwargs):
        """
        根据 id 删除项目分组
        """

        parse_data(request, 'DELETE')
        id = kwargs['pk']
        group = get_by_id(id)
        # 是否被项目使用
        try:
            from backend.handler.project.project import count_by_group
        except ImportError:
            raise PlatformError.error(ErrorCode.FAIL)
        count = count_by_group(id)
        if count > 0:
            raise PlatformError.error(ErrorCode.PROJECT_GROUP_HAS_PROJECT)
        group.delete()
        return Response.def_success()

    def update(self, request, *args, **kwargs):
        """
        修改项目分组
        """

        body = parse_data(request, 'PUT')
        id, name = get_params(body, 'id', 'name').values()
        group = get_by_id(id)
        update_fields(group, name=name)
        save(group)
        return Response.success(group)

    def list(self, request, *args, **kwargs):
        """
        分页查询项目分组

        可根据 name 模糊查询
        """

        data = parse_data(request, 'GET')
        page, page_size, name = page_params(data, 'name').values()
        groups = ProjectGroup.objects.owner().contains(name=name)
        page_group = Paginator(groups, page_size)
        result = page_group.page(page)
        return Response.success(result)


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询分组详情
    """

    try:
        group = ProjectGroup.objects.owner().get(id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error_args(ErrorCode.DATA_NOT_EXISTED, '项目分组', 'id')
    return group


def get_list_by_ids(ids):
    """
    根据 id 数组查询
    """

    return ProjectGroup.objects.owner().fields_in(id=ids)
