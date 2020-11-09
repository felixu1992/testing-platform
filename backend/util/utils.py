import json
from django.http import QueryDict
from backend.util.jwt_token import UserHolder
from testing_platform.settings import LOGGER
from backend.exception import ErrorCode, PlatformError


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


def get_params(data, *args, toleration=True):
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


def get_params_dict(data, *args, toleration=True):
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
                LOGGER.info('参数获取失败，填充为 None，data={}，中不包含 {}', data, param)
                result.update({param: None})
            # 不容忍则报错
            else:
                LOGGER.error('参数获取失败，data={}，中不包含 {}', data, param)
                raise PlatformError.error_args(ErrorCode.MISSING_NECESSARY_KEY, param)
    return result


def page_params_dict(data, *args):
    """
    取分页查询参数

    一般分页查询对所有可查询参数均容忍不存在
    分页参数不存在的话默认使用 page 为 1，page_size 为 10 作为分页条件
    """

    # 取字典中的分页参数
    result = get_params_dict(data, 'page', 'page_size', *args)
    # 不存在则填充默认值
    # if page is None or int(page) <= 0:
    #     page = 1
    # if page_size is None or int(page_size) <= 0:
    #     page_size = 10
    # return page, page_size, *values
    return result


def page_params(data, *args):
    """
    取分页查询参数

    一般分页查询对所有可查询参数均容忍不存在
    分页参数不存在的话默认使用 page 为 1，page_size 为 10 作为分页条件
    """

    # 取字典中的分页参数
    page, page_size, *values = get_params(data, 'page', 'page_size', *args)
    # 不存在则填充默认值
    if page is None or int(page) <= 0:
        page = 1
    if page_size is None or int(page_size) <= 0:
        page_size = 10
    return page, page_size, *values


def update_fields(obj, always=False, **kwargs):
    """
    更新对象中的属性

    通过 always 空值是否可更新空值
    """

    if obj is None or isinstance(obj, object):
        return
    for field, value in kwargs.items():
        # 总是更新，更新所有值
        if always:
            setattr(obj, field, value)
        # 只更新非空值
        elif not always and value:
            setattr(obj, field, value)


# --------------------------------------------- 对 Django 的 QuerySet 进行封装 -------------------------------------------

def str_is_none(source):
    """
    判断字符串不为空
    """
    if source == '' or source == 'NULL' or source == 'None' or source is None:
        return True
    return False


def get_value(source, steps):
    """
    根据入参字典以及取值步骤取出结果

    取值步骤为 . 连接，如：data.records.0.name 含义为取 data 下 records 列表的第 0 条的 name 字段的值
    """
    # 分割取值步骤为列表
    keys = steps.split(".")
    try:
        # 循环取值步骤字典
        for i in range(0, len(keys)):
            # 取字段值
            key = keys[i]
            # 如果为数字则转为数字(数字代表从列表取值)，否则为字符
            key = key if not key.isdigit() else int(key)
            # 从结果字典取值
            source = source[key]
    # 出现异常直接填充为空字符
    except KeyError:
        return None
    return source


def set_value(value, target, steps):
    # 以 . 分割插入步骤为数组
    keys = steps.split(".")
    # 循环找到对应位置插入
    for i in range(0, len(keys)):
        key = keys[i]
        # 如果当前步骤为字符串类型的数字，转为 int
        key = key if not key.isdigit() else int(key)
        # 取到最后了，直接将值插入该位置
        if i == len(keys) - 1:
            target[key] = value
        # 否则继续往下找插入位置
        else:
            try:
                # 从目标中取当前 key 对应的值为下一次的目标
                target = target[key]
            except KeyError:
                # 报错则下一次目标为空字典
                target.update({key: {}})
                target = target[key]