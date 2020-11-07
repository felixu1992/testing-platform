import json

from django.http import QueryDict

from backend.util.jwt_token import UserHolder
from testing_platform.settings import LOGGER
from backend.exception.error_code import ErrorCode
from backend.exception.exception import PlatformError


def full_data(request, method):
    """
    从请求中获取请求体
    """
    # 判断请求方法是否符合要求
    data = {}
    if request.method != method:
        raise PlatformError.error_args(ErrorCode.HTTP_METHOD_NOT_SUPPORTED, method)
    # POST 和 PUT json 从 body 中取 form data 从 POST 中取
    if method == 'POST' or method == 'PUT':
        if request.content_type == 'application/json':
            data = json.loads(str(request.body, 'utf-8'))
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


def get_params(data, *args, toleration=False):
    """
    从字典 data 中取 args 中的字段值

    容忍度决定着是否报错
    """
    # 作为取值函数，data 和 args 理应均不为空
    if data is None or not isinstance(data, dict) or args is None:
        raise PlatformError.error(ErrorCode.VALIDATION_ERROR)
    # 结果集
    values = []
    # 遍历需要取出的关键字
    for param in args:
        try:
            # 取出结果并追加
            value = data[param]
            values.append(value)
        except KeyError:
            # 字典中不存在，容忍则追加 None
            if toleration:
                LOGGER.info('参数获取失败，填充为 None，data={}，中不包含 {}', data, param)
                values.append(None)
            # 不容忍则报错
            else:
                LOGGER.error('参数获取失败，data={}，中不包含 {}', data, param)
                raise PlatformError.error_args(ErrorCode.MISSING_NECESSARY_KEY, param)
    return values


def page_params(data, *args):
    """
    取分页查询参数

    一般分页查询对所有可查询参数均容忍不存在
    分页参数不存在的话默认使用 page 为 1，page_size 为 10 作为分页条件
    """
    # 取字典中的分页参数
    page, page_size, *values = get_params(data, 'page', 'page_size', *args, toleration=True)
    # 不存在则填充默认值
    if page is None or int(page) <= 0:
        page = 1
    if page_size is None or int(page_size) <= 0:
        page_size = 10
    return page, page_size, *values
