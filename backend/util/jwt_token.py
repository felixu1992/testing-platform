import threading
import time
import jwt
from jwt import DecodeError


class Security:
    @staticmethod
    def encode(data):
        """
        生成 jwt token
        """
        payload = {
            'data': data,
            'timestamp': int(time.time() * 1000)
        }
        jwt_token = jwt.encode(payload, "testingplatformhs256", algorithm="HS256")
        return bytes.decode(jwt_token)

    @staticmethod
    def decode(jwt_token):
        """
        解析 jwt token
        """
        try:
            return jwt.decode(jwt_token, verify=False)
        except DecodeError:
            return None


class UserHolder:
    # 创建全局ThreadLocal对象:
    local = threading.local()

    @staticmethod
    def cache_user(key):
        """
        缓存当前的用户标识符
        """
        UserHolder.local.principle = key

    @staticmethod
    def current_user():
        """
        获取当前用户
        """
        try:
            return UserHolder.local.principle
        except AttributeError:
            return None

    @staticmethod
    def cache_token(token):
        """
        缓存当前的用户 token
        """
        UserHolder.local.token = token

    @staticmethod
    def current_token():
        """
        获取当前用户 token
        """
        try:
            return UserHolder.local.token
        except AttributeError:
            return None
