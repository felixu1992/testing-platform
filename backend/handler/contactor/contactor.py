from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.core.paginator import Paginator
from rest_framework import serializers, viewsets
from rest_framework.decorators import action

from backend.exception import ErrorCode, ValidateError, PlatformError
from backend.models import Contactor
from backend.util import Response, parse_data, get_params, update_fields, page_params


class ContactorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contactor
        fields = ['id', 'name', 'email', 'phone', 'group_id', 'created_at', 'updated_at']


class ContactorViewSet(viewsets.ModelViewSet):
    queryset = Contactor

    serializer_class = ContactorSerializer

    def post(self, request):
        """
        创建联系人
        """

        body = parse_data(request, 'POST')
        contactor = Contactor(**body)
        try:
            contactor.full_clean()
        except ValidationError as e:
            raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
        contactor.save()
        return Response.success(contactor)

    def delete(self, request, id):
        """
        根据 id 删除联系人
        """

        parse_data(request, 'DELETE')
        contactor = get_by_id(id)
        # TODO 判断是否被用例使用
        contactor.delete()
        return Response.def_success()

    def put(self, request):
        """
        修改联系人
        """

        data = parse_data(request, 'PUT')
        params_dict = get_params(data, 'id', 'name', 'phone', 'email')
        contractor = get_by_id(params_dict['id'])
        update_fields(contractor, **params_dict)
        try:
            contractor.full_clean()
        except ValidationError as e:
            raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
        contractor.save()
        return Response.success(contractor)

    @action(methods=['GET'], detail=False, url_path='page')
    def page(request):
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
        page_contactors.page(page)
        return Response.success(page_contactors)


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询联系人详情
    """

    try:
        contactor = Contactor.objects.owner().get(id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    return contactor


def count_by_group(group_id):
    """
    根据分组 id 计数
    """

    return Contactor.objects.owner().filter(group_id=group_id).count()
