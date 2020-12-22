import re

from backend.util.jwt_token import UserHolder
from backend.exception import ErrorCode, ValidateError, PlatformError
from backend.util.resp_data import Response
from backend import LOGGER
from django.core.cache import cache

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

ignores = [re.compile('^/$'), re.compile('/user/signin'), re.compile('js$'), re.compile('css$'), re.compile('swagger')]


class RequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        """
        校验 token

        1. 忽略部分路径规则
        2. 解析出 token 缓存当前用户
        """

        allowed = False
        for ignore in ignores:
            if re.match(ignore, request.path):
                allowed = True
                break

        # 不被忽略则按规则校验
        if not allowed:
            # 取出请求头，失败跳回首页
            headers = request.headers
            try:
                token = headers['Authorization']
            except KeyError:
                return Response.failed(ErrorCode.REQUIRE_LOGIN)
            # 认证信息不以 token 开头重定向会首页
            if not token.startswith('token '):
                return Response.failed(ErrorCode.MISSING_AUTHORITY)
            # 取真实 token
            token = token.replace('token ', '', 1)
            # 取 token 的缓存
            user_id = cache.get(token)
            # 不存在则 token 过期，跳首页
            if not user_id:
                return Response.failed(ErrorCode.REQUIRE_LOGIN)
            # 重置过期时间
            cache.expire(token, timeout=60 * 60 * 24 * 7)
            # 缓存当前用户 id
            UserHolder.cache_user(user_id)

    def process_response(self, request, response):
        """
        统一返回封装
        """
        return response


class ExceptionMiddleware(MiddlewareMixin):
    """
    统一异常处理
    """

    def process_exception(self, request, exception):
        # 自定义异常
        if isinstance(exception, PlatformError):
            return Response.failed(exception)
        # 校验失败
        if isinstance(exception, ValidateError):
            return Response.failed(exception)
        # 其他异常
        else:
            LOGGER.error(exception)
            return Response.failed(ErrorCode.FAIL)
