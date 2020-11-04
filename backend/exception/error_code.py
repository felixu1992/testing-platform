from enum import Enum


class ErrorCode(Enum):
    """
    错误码枚举
    """

    OK = 0, '请求成功'
    FAIL = -1, '发生未知错误，请稍后再试'
    HTTP_METHOD_NOT_SUPPORTED = 100, '当前请求仅支持 {} 方法'
    LOGIN_FAILED = 101, '登录失败，请检查用户名或密码是否正确'
    VALIDATION_ERROR = 102, '参数校验失败'
    DATA_NOT_EXISTED = 103, '当前数据不存在，请检查数据是否正确'
    MISSING_NECESSARY_KEY = 104, '缺少必要参数: {}'

    def __init__(self, code, message):
        self.code = code
        self.message = message
