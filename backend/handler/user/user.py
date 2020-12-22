import hashlib
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseRedirect
from rest_framework import serializers, viewsets
from rest_framework.decorators import action

from backend.models import User
from backend.util import Security, UserHolder, Response, parse_data, get_params
from django.core.cache import cache
from backend.exception.exception import PlatformError
from backend.exception import ErrorCode


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'role', 'email', 'phone', 'password', 'avatar', 'created_at', 'updated_at']


class UserViewSet(viewsets.GenericViewSet):

    queryset = User

    serializer_class = UserSerializer

    @action(methods=['POST'], detail=False, url_path='signin')
    def login(self, request):
        """
        登录

        根据邮箱和密码登录
        """
        data = parse_data(request, 'POST')
        # 邮箱，密码
        email, password = get_params(data, 'email', 'password').values()
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

    @action(methods=['POST'], detail=False, url_path='signout')
    def logout(self, request):
        """
        登出

        将清除用户信息
        """
        # 找到当前 token
        token = UserHolder.current_token()
        # 删除 token
        if cache.has_key(token):
            # 直接过期
            cache.expire(0)
        return HttpResponseRedirect('/')

    def register(self, request):
        pass

# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------
