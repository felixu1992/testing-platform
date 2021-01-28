import json

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.paginator import Paginator
from rest_framework import serializers, viewsets
from rest_framework.decorators import action

from backend.exception import ErrorCode, PlatformError, ValidateError
from backend.models import Report
from backend.util import UserHolder, Response, parse_data, page_params, save


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'name', 'created_at', 'updated_at']


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report

    serializer_class = ReportSerializer

    def list(self, request, *args, **kwargs):
        """
        分页查询项目

        可全量分页(当然只有自己的数据)
        可传入分组
        可传入 name 模糊
        """

        data = parse_data(request, 'GET')
        page, page_size, name, record_id, status = page_params(data, 'name', 'record_id', 'status').values()
        if record_id is None:
            raise PlatformError.error_args(ErrorCode.MISSING_NECESSARY_KEY, 'record_id')
        projects = Report.objects.filter(owner=UserHolder.current_user()).exact(record_id=record_id)\
            .contains(name=name).exact(status=status)
        page_projects = Paginator(projects, page_size)
        result = page_projects.page(page)
        return Response.success(result)

    def retrieve(self, request, *args, **kwargs):
        """
        根据 id 查询项目详细信息
        """

        parse_data(request, 'GET')
        report = get_by_id(kwargs['pk'])
        decoding(report)
        return Response.success(report)


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询项目
    """

    try:
        report = Report.objects.get(owner=UserHolder.current_user(), id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error_args(ErrorCode.DATA_NOT_EXISTED, '用例报告', 'id')
    return report


def create(report):
    """
    创建用例结果
    """

    save(report)
    return report


def decoding(report):
    """
    对部分参数进行解码操作
    """

    if report.extend_keys:
        report.extend_keys = json.loads(report.extend_keys)
    if report.extend_values:
        report.extend_values = json.loads(report.extend_values)
    if report.expected_keys:
        report.expected_keys = json.loads(report.expected_keys)
    if report.expected_values:
        report.expected_values = json.loads(report.expected_values)
