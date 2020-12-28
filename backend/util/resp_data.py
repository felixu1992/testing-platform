import datetime

from django.core.paginator import Paginator, Page
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import Model
from django.forms import model_to_dict
from django.http.response import JsonResponse
from backend.exception import ErrorCode


class ExtendedEncoder(DjangoJSONEncoder):
    """
    重写反序列化方法
    """

    def default(self, obj):
        # Model 对象转字典，且排除 password 和 owner 字段的返回
        if isinstance(obj, Model):
            return obj_to_dict(obj, exclude=['password', 'owner'])
        # Paginator 对象转字典，针对分页情况
        if isinstance(obj, Page):
            return page_to_dict(obj)
        # 都不是，采用默认父类序列化方式
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        return super().default(obj)


def page_to_dict(obj):
    paginator = obj.paginator
    return {
        'page': obj.number,
        'page_size': paginator.per_page,
        'pages': paginator.num_pages,
        'count': paginator.count,
        'records': list(obj.object_list)
    }


def obj_to_dict(obj, exclude=None):
    """
    调用 from django.db.models import Model#model_to_dict() 完成 Model 原有字段的转换
    然后手动完成其他添加字段的转换
    """
    data = model_to_dict(obj, exclude=exclude)
    # 对象转字典
    properties = obj.__dict__
    # 遍历对象字典
    for k, v in properties.items():
        # 已经转过的字段和 _ 开头的属性不处理
        if k in data.keys() or k.startswith('_'):
            continue
        # 需要排除的字段不处理
        if exclude and k in exclude:
            continue
        # 其他字段添加入字典
        data[k] = v
    return data


class Response(JsonResponse):
    """
    提供成功和失败的快速统一结构封装
    """

    def __init__(self, data, error, passed):
        super().__init__(self.__result(data, error, passed), encoder=ExtendedEncoder)

    def __result(self, data, error, passed):
        """
        生成统一返回结果
        """
        result = {
            'code': error.code,
            'message': error.message
        }
        # 成功且有数据返回，在字典中插入 data
        if passed and data is not None:
            data = list(data) if isinstance(data, list) else data
            result.update({'data': data})
        return result

    @staticmethod
    def def_success():
        """
        无返回的成功
        """
        return Response.success(None)

    @staticmethod
    def success(data):
        """
        返回 data 的成功
        """
        return Response(data=data, error=ErrorCode.OK, passed=True)

    @staticmethod
    def failed(error):
        """
        失败
        """
        return Response(data=None, error=error, passed=False)
