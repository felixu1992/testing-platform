from enum import Enum


class ErrorCode(Enum):
    """
    错误码枚举
    """

    # 通用状态码
    OK = 0, '请求成功'
    FAIL = -1, '发生未知错误，请稍后再试'
    HTTP_METHOD_NOT_SUPPORTED = 100, '当前请求仅支持 {} 方法'
    LOGIN_FAILED = 101, '登录失败，请检查用户名或密码是否正确'
    VALIDATION_ERROR = 102, '参数校验失败'
    DATA_NOT_EXISTED = 103, '{} 根据 {} 查询的数据不存在，请检查入参是否正确'
    MISSING_NECESSARY_KEY = 104, '缺少必要参数: {}'
    MISSING_AUTHORITY = 105, '请检查您是否具有访问此地址的权限'
    REQUIRE_LOGIN = 106, '请(重新)登录'

    # 联系人
    CONTACTOR_GROUP_HAS_CONTACTOR = 10000, '联系人分组下存在联系人，无法删除'

    # 文件
    FILE_GROUP_HAS_FILE = 20000, '文件分组下存在文件，无法删除'

    # 项目
    PROJECT_GROUP_HAS_PROJECT = 30000, '文件分组下存在文件，无法删除'
    PROJECT_NOT_HAVE_CASES = 30001, '当前项目没有可执行用例，已忽略执行'

    # 用例
    CASE_CREATE_REPORT_FAILED = 40000, '用例执行生成结果失败，请稍后再试'
    EXPECTED_NOT_ALLOWED = 40001, '预期字段和预期值个数不匹配'
    DEPEND_NOT_ALLOWED = 40002, '依赖参数和依赖取值个数不匹配'

    def __init__(self, code, message):
        self.code = code
        self.message = message
