import hashlib
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from backend.models import User
from backend.util import Security, UserHolder, Response, full_data
from django.core.cache import cache
from backend.exception.exception import PlatformError
from backend.exception import ErrorCode


def login(request):
    body = full_data(request, 'POST')
    # 邮箱，密码
    email = body['email']
    password = body['password']
    # 密码 md5
    # TODO 前端 md5 更加安全
    hl = hashlib.md5()
    hl.update(password.encode(encoding='utf-8'))
    password = hl.hexdigest()
    # 查询用户
    try:
        user = User.objects.get(email=email, password=password)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.LOGIN_FAILED)
    if user:
        # 生成 token
        token = Security.encode(user.id)
        user.password = token
        user.token = token
        # token 5 分钟有效
        cache.set(token, user.id, timeout=60 * 60 * 24 * 7)
        return Response.success(user)


def logout(request):
    """
    登出
    """
    # 找到当前 token
    token = UserHolder.current_token()
    # 删除 token
    if cache.has_key(token):
        # 直接过期
        cache.expire(0)
    return HttpResponseRedirect('/')
