class PlatformError(Exception):
    """
    全局自定义异常
    """

    def __init__(self, code, message):
        self.code = code
        self.message = message

    @staticmethod
    def error(error):
        return PlatformError(error.code, error.message)

    @staticmethod
    def error_args(error, *args):
        message = error.message.format(*args)
        return PlatformError(error.code, message)


class ValidateError(Exception):
    """
    校验异常
    """
    def __init__(self, code, message):
        self.code = code
        self.message = message

    @staticmethod
    def error(error, *args):
        message = {}
        for i in range(1, len(args) + 1):
            message[str(i)] = args[i - 1]
        return ValidateError(error.code, message)
