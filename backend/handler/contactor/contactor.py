from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework import serializers, viewsets
from backend.exception import ErrorCode, PlatformError
from backend.models import Contactor
from backend.handler.contactor import contactor_group
from backend.util import Response, parse_data, get_params, update_fields, page_params, save


class ContactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contactor
        fields = ['id', 'name', 'email', 'phone', 'group_id', 'created_at', 'updated_at']


class ContactorViewSet(viewsets.ModelViewSet):
    queryset = Contactor.objects

    serializer_class = ContactorSerializer

    def create(self, request, *args, **kwargs):
        """
        新增联系人

        创建一个新的联系人
        """

        body = parse_data(request, 'POST')
        contactor = Contactor(**body)
        # 校验分组是否存在
        contactor_group.get_by_id(contactor.group_id)
        save(contactor)
        return Response.success(contactor)

    def destroy(self, request, *args, **kwargs):
        """
        删除联系人

        根据 id 删除联系人
        """

        parse_data(request, 'DELETE')
        id = kwargs['pk']
        contactor = get_by_id(id)
        # TODO 判断是否被用例使用
        contactor.delete()
        return Response.def_success()

    def update(self, request, *args, **kwargs):
        """
        修改联系人

        更新联系人信息
        """

        data = parse_data(request, 'PUT')
        params_dict = get_params(data, 'id', 'name', 'phone', 'email')
        contactor = get_by_id(params_dict['id'])
        update_fields(contactor, **params_dict)
        # 校验分组是否存在
        contactor_group.get_by_id(contactor.group_id)
        save(contactor)
        return Response.success(contactor)

    def list(self, request, *args, **kwargs):
        """
        分页查询联系人

        可全量分页(当然只有自己的数据)
        可传入分组
        可传入 name 模糊
        可传入 phone 模糊
        可传入 email 模糊
        """

        data = parse_data(request, 'GET')
        page, page_size, name, phone, email = page_params(data, 'name', 'phone', 'email').values()
        contactors = Contactor.objects.owner().contains(name=name, phone=phone, email=email)
        page_contactors = Paginator(contactors, page_size)
        result = page_contactors.page(page)
        # 得到所有分组 id
        group_ids = [o.group_id for o in result.object_list]
        group_names = {}
        groups = contactor_group.get_list_by_ids(group_ids)
        for group in groups:
            group_names.update({group.id: group.name})
        for contactor in result.object_list:
            group_name = group_names[contactor.group_id]
            if group_name:
                contactor.group_name = group_name
        return Response.success(result)


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询联系人详情
    """

    try:
        contactor = Contactor.objects.owner().get(id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error_args(ErrorCode.DATA_NOT_EXISTED, '联系人', 'id')
    return contactor


def count_by_group(group_id):
    """
    根据分组 id 计数
    """

    return Contactor.objects.owner().filter(group_id=group_id).count()


def get_list_by_ids(ids):
    """
    根据 id 数组查询
    """

    return Contactor.objects.owner().fields_in(id=ids)
