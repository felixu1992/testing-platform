import json

from django.core.exceptions import ValidationError
from django.http import QueryDict
from backend.util.jwt_token import UserHolder
from backend import LOGGER
from backend.exception import ErrorCode, PlatformError, ValidateError


def parse_data(request, method):
    """
    从请求中解析请求体得到数据
    """

    # 判断请求方法是否符合要求
    data = {}
    if request.method != method:
        raise PlatformError.error_args(ErrorCode.HTTP_METHOD_NOT_SUPPORTED, method)
    # POST 和 PUT json 从 body 中取 form data 从 POST 中取
    if method == 'POST' or method == 'PUT':
        if 'application/json' in request.content_type:
            # application/json;charset=xxx
            json_encoding = get_encoding(request.content_type)
            data = json.loads(str(request.body, json_encoding))
        else:
            data = request.POST
    # DELETE 和 GET 从 GET 中取
    if method == 'GET' or method == 'DELETE':
        data = request.GET
    # 遍历重新插值，因为如果然后是 QueryDict 直接调用对象构造函数后，数据类型不匹配
    result = {}
    if isinstance(data, QueryDict):
        for key, value in data.items():
            result.update({key: value})
    else:
        result = data
    result.update({'owner': UserHolder.current_user()})
    return result


def get_encoding(content_type):
    # application/json;charset=xxx
    split = content_type.split(';')
    if len(split) <= 1:
        return 'utf-8'
    else:
        # charset=xxx
        charset_pair = split[1]
        pair_split = charset_pair.split('=')
        if len(pair_split) > 1:
            return pair_split[1]
        else:
            return 'utf-8'


def get_params(data, *args, toleration=True):
    """
    从字典 data 中取 args 中的字段值

    容忍度决定着是否报错
    """

    # 作为取值函数，data 和 args 理应均不为空
    if data is None or not isinstance(data, dict) or args is None:
        raise PlatformError.error(ErrorCode.VALIDATION_ERROR)
    # 结果集
    result = {}
    # 遍历需要取出的关键字
    for param in args:
        try:
            # 取出结果并追加
            value = data[param]
            result.update({param: value})
        except KeyError:
            # 字典中不存在，容忍则追加 None
            if toleration:
                # LOGGER.info('参数获取失败，填充为 None，data={}，中不包含 {}', data, param)
                result.update({param: None})
            # 不容忍则报错
            else:
                # LOGGER.error('参数获取失败，data={}，中不包含 {}', data, param)
                raise PlatformError.error_args(ErrorCode.MISSING_NECESSARY_KEY, param)
    return result


def page_params(data, *args):
    """
    取分页查询参数

    一般分页查询对所有可查询参数均容忍不存在
    分页参数不存在的话默认使用 page 为 1，page_size 为 10 作为分页条件
    """

    # 取字典中的分页参数
    result = get_params(data, 'page', 'page_size', *args)
    try:
        page = result['page']
        if page is None or int(page) <= 0:
            result['page'] = 1
    except KeyError:
        result.update({'page': 1})
    try:
        page_size = result['page_size']
        if page_size is None or int(page_size) <= 0:
            result['page_size'] = 10
    except KeyError:
        result.update({'page_size': 10})
    return result


def update_fields(obj, always=True, **kwargs):
    """
    更新对象中的属性

    通过 always 空值是否可更新空值
    """

    if obj is None or not isinstance(obj, object):
        return
    for field, value in kwargs.items():
        # 总是更新，更新所有值
        if always:
            setattr(obj, field, value)
        # 只更新非空值
        elif not always and value:
            setattr(obj, field, value)


def filter_obj_single(objs, key, value):
    """
    通过对象中的某个 key 过滤列表对象

    只返回一个
    """
    obj = [obj for obj in objs if getattr(obj, key) == value]
    return obj[0]


def save(entity):
    """
    保存对象信息

    Django 往数据库存储信息
    """

    try:
        entity.full_clean()
    except ValidationError as e:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, *e.messages)
    entity.save()


def batch_save(objects, objs):
    """
    批量新增
    """

    objects.bulk_create(objs)


def batch_update(objects, objs, fields):
    """
    批量新增
    """

    objects.bulk_update(objs, fields=fields)
