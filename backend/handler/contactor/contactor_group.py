from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from itertools import groupby
from backend.exception import ErrorCode, PlatformError
from backend.models import ContactorGroup
from backend.util import Response, get_params, parse_data, page_params, update_fields, save


class ContactorGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactorGroup
        fields = ['id', 'name', 'created_at', 'updated_at']


class ContactorGroupViewSet(viewsets.ModelViewSet):
    queryset = ContactorGroup.objects

    serializer_class = ContactorGroupSerializer

    def create(self, request, *args, **kwargs):
        """
        创建联系人分组
        """

        body = parse_data(request, 'POST')
        group = ContactorGroup(**body)
        save(group)
        return Response.success(group)

    def destroy(self, request, *args, **kwargs):
        """
        根据 id 删除联系人分组
        """

        parse_data(request, 'DELETE')
        id = kwargs['pk']
        group = get_by_id(id)
        # 判断是否被联系人使用
        try:
            from backend.handler.contactor.contactor import count_by_group
        except ImportError:
            raise PlatformError.error(ErrorCode.FAIL)
        count = count_by_group(id)
        if count > 0:
            raise PlatformError.error(ErrorCode.CONTACTOR_GROUP_HAS_CONTACTOR)
        group.delete()
        return Response.def_success()

    def update(self, request, *args, **kwargs):
        """
        修改联系人分组
        """

        body = parse_data(request, 'PUT')
        id, name = get_params(body, 'id', 'name').values()
        group = get_by_id(id)
        update_fields(group, name=name)
        save(group)
        return Response.success(group)

    def list(self, request, *args, **kwargs):
        """
        分页查询联系人分组

        可根据 name 做模糊
        """

        data = parse_data(request, 'GET')
        page, page_size, name = page_params(data, 'name').values()
        groups = ContactorGroup.objects.owner().contains(name=name)
        page_group = Paginator(groups, page_size)
        result = page_group.page(page)
        return Response.success(result)

    @action(methods=['GET'], detail=False, url_path='tree')
    def tree(self, request):
        parse_data(request, 'GET')
        groups = ContactorGroup.objects.owner().all()
        try:
            from backend.handler.contactor.contactor import get_list_by_groupIds
        except ImportError:
            raise PlatformError.error(ErrorCode.FAIL)
        group_ids = [group.id for group in groups]
        contactors = get_list_by_groupIds(group_ids)
        contactor_map = {k: list(v) for k, v in groupby(contactors, lambda contactor: contactor.group_id)}
        result = []
        for group in groups:
            result.append({
                'title': group.name,
                'value': 'group' + str(group.id),
                'key': 'group' + str(group.id),
                'disabled': True,
                'children': list(map(lambda o: {
                    'title': o.name,
                    'value': o.id,
                    'key': o.id,
                    'children': []
                }, contactor_map.get(group.id))) if contactor_map.get(group.id) else []
            })
        return Response.success(result)


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询
    """

    try:
        group = ContactorGroup.objects.owner().get(id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error_args(ErrorCode.DATA_NOT_EXISTED, '联系人分组', 'id')
    return group


def get_list_by_ids(ids):
    """
    根据 id 数组查询
    """

    return ContactorGroup.objects.owner().fields_in(id=ids)
