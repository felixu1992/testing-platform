import json
import re
import time
import requests
from requests import Response
from backend.models import Report
from backend.util import filter_obj_single, PlatformError, ErrorCode
from backend.handler import file
from backend import CONTENT_TYPE, APPLICATION_JSON, FORM_DATA, LOGGER
from backend.settings import *


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


class Executor:

    def __init__(self, case_infos, project):
        self.case_infos = case_infos
        self.project = project
        self.reports = []
        for case_info in case_infos:
            self.reports.append(Report(case_info.__dict__.copy()))

    def execute(self):
        """
        执行用例
        """

        # 循环执行用例
        if self.case_infos:
            for case_info in self.case_infos:
                self.__do_execute(case_info)
        return self.reports

    def __do_execute(self, case_info):
        """
        执行请求

        1. 判断是否执行
        2. 执行需要构建请求参数
        3. 填充报告
        """

        # 过滤出结果
        report = filter_obj_single(self.reports, 'id', case_info.id)
        # 如果为空则添加一个结果
        if report is None:
            raise PlatformError.error(ErrorCode.CASE_CREATE_REPORT_FAILED)
        # 不执行的用例直接返回
        if not case_info.run:
            report.status = IGNORED
            return

        # 构建请求参数
        request = self.__build_request(case_info)
        if request:
            url, headers, params, files, result = request
        else:
            return
        # 请求开始时间
        start = time.time()
        # 请求
        result = self.__do_request(url, headers, params, files, result, case_info)
        # 计算请求耗时
        time_used = int((time.time() - start) * 1000)
        # 校验结果
        self.__check_status(report, result, time_used)
        # print 结果
        self.__print_result(report, url)

    def __build_request(self, case_info):
        """
        构建请求需要的一些内容

        1. headers
        2. params
        3. url
        """

        # 构建请求头
        headers = self.__build_header(case_info)

        # 构建参数
        params, files = self.__build_params(case_info, headers)

        # 预先构建结果
        result = {'code': -100, 'message': '预填充错误结果'}

        # 构建 url
        url = self.__build_url(case_info, result)
        return url, headers, params, files, result

    def __build_header(self, case_info):
        # 构建请求头，如果所属项目有头信息
        headers = {}
        # 父级 header
        if self.project and self.project.headers:
            headers.update(self.project.headers)
        if case_info.headers:
            headers.update(case_info.headers)
        return headers

    def __build_params(self, case_info, headers):
        # 得到请求参数
        self.__parse_param(case_info)
        params = case_info.params
        # 定义一个字典，在文件上传时使用
        files = {}
        if case_info.headers:
            headers.update(case_info)
        # 请求头没有 Content-Type 默认 json
        if CONTENT_TYPE not in headers or headers[CONTENT_TYPE] == APPLICATION_JSON:
            # 设置为 json
            headers.update({CONTENT_TYPE: APPLICATION_JSON})
            # 将字典转为字符串
            params = json.dumps(case_info.params).encode('utf-8').decode('latin-1')
        # 有 multipart/form-data 的 Content-Type 认为很有可能有文件上传
        elif headers[CONTENT_TYPE] == FORM_DATA:
            # 上传文件时不需要显示设置 Content-Type
            headers.pop(CONTENT_TYPE)
            # 循环 params 字典
            has_file = False
            for key, value in params.items():
                # 若值为字符串，并且以 file: 开头，则认为为文件上传
                if isinstance(value, str) and value.startswith('file:'):
                    # 以二进制流加载到 files 中
                    try:
                        f = file.get_by_id(value.replace('file:', '', 1))
                        files.update({key: open(f.path, 'rb')})
                        has_file = True
                    except IOError:
                        files.update({key: None})
            # 如果 form-data 且不含文件，需要单独处理
            if not has_file:
                for p, v in params.items():
                    params[p] = (None, v)
        return params, files

    def __build_url(self, case_info, result):
        if (self.project is None or self.project.host is None) and case_info.host is None:
            result.update({'message': 'host 不能为空'})
            case_info.response_content = '请求路径缺失，接口未执行'
            return None
        if self.project and self.project.host:
            case_info.host = self.project.host
        self.__parse_path(case_info)
        url = case_info.host + case_info.path
        return url

    def __do_request(self, url, headers, params, files, result, case_info):
        """
        实际请求用例
        """

        # 请求接口
        method = case_info.method
        try:
            # POST
            if method == 'post':
                response = requests.post(url, data=params, headers=headers, files=files)
                result = response.json()
            # GET
            elif method == "get":
                response = requests.get(url, data=params, headers=headers)
                result = response.json()
            # DELETE
            elif method == "delete":
                response = requests.delete(url, data=params, headers=headers)
                result = response.json()
            # PUT
            elif method == "put":
                response = requests.put(url, data=params, headers=headers, files=files)
                result = response.json()
            # 未知方法
            else:
                response = Response()
                response.status_code = 200
                result.update({'message': '请求方法不支持，请检查用例'})
            result.update({'http_code': response.status_code})
            # 请求非 200 不处理
            # if response.status_code != 200:
            #     result = {'code': '-1', 'message': '请求失败，请检查用例的请求路径、请求方法、请求参数是否正确'}
        except Exception:
            result.update({'message': '请求失败，请检查用例的请求路径、请求方法、请求参数是否正确'})
        return result

    def __check_status(self, report, result, time_used):
        """
        校验结果

        思路：
        先判断是否需要校验 HTTP CODE，如果需要，且校验失败，则后续直接忽略
        让预期值为一个字典
        实际值为另一个字典
        对比字典内容是否一致，从而确定结果是否符合预期
        """

        report.time_used = time_used

        # 校验 Http Code
        report.status = FAILED
        report.http_status = result['http_code']
        if report.check_status and report.http_status != report.expected_http_status:
            return
        code = result['code']
        # 防止 code 为字符串类型的数字
        report.response_code = code if isinstance(code, int) else int(code)

        # 定义预期和结果字典
        expected = {}
        response = {}
        # 预期字段以 , 分割为预期字段的列表
        expected_keys = report.expected_key.split(',')
        # 预期结果以 , 分割为预期结果的列表
        expected_values = str(report.expected_value).split(',')
        # 校验步骤以 , 分割为列表
        check_steps = report.check_step.split(',')
        # 循环预期字段的个数
        for i in range(0, len(expected_keys)):
            # 将预期字段对应的预期值以 : 分割，得到预期值的取值过程列表
            row_steps = expected_values[i].split(":")
            # 如果预期值直接给出，则 row_steps 长度为 1
            if len(row_steps) == 1:
                # 将预期字段以及预期值放入预期字典
                expected.update({expected_keys[i]: row_steps[0]})
            else:
                # 取依赖的行数据
                ci = [ci for ci in self.reports if getattr(ci, 'id') == int(row_steps[0])]
                ci = ci[0]
                # 没取到直接判定失败
                if not ci:
                    report.status = 'failed'
                    return
                # 否则按照依赖步骤取出依赖值，填充预期字典
                ci = json.loads(getattr(ci, 'response_content'))
                expected.update({expected_keys[i]: get_value(ci, row_steps[1])})
            # 将预期字段对应的结果从结果中取出(由于这种情况)
            response.update({expected_keys[i]: str(get_value(result, check_steps[i]))})
        # 填入结果
        if expected == response:
            report.status = PASSED
        else:
            report.status = FAILED
        # result.pop('ignore')
        # result.pop('http_code')
        # 填充结果到用例对象中
        report.response_content = json.dumps(result, ensure_ascii=False)

    def __print_result(self, report, url):
        """
        打印请求结果
        """

        out = json.dumps({'用例名称': report.name, '用例描述': report.description, '请求方式': report.method, '请求路径': url,
                          '请求结果': report.status}, indent=2, ensure_ascii=False)
        if report.status == 'passed':
            out = out.replace('passed', '\033[0;33;42m' + 'passed' + '\033[0m')
        else:
            out = out.replace('failed', '\033[0;37;41m' + 'failed' + '\033[0m')
        LOGGER.info(out)

    def __parse_param(self, case_info):
        """
        用于解析当前用例信息中参数需要的占位符

        即将 ex_keys 中的字段，以及 ex_values 中的值解析到 params 中
        """

        # 获取当前用例的 params
        params = getattr(case_info, 'params')
        params = {} if params is None else json.loads(params)
        # 取当前用例的 ex_keys
        ex_keys = getattr(case_info, 'ex_keys')
        # 如果有需要处理的占位符
        if ex_keys != '' and ex_keys is not None:
            # 以 , 分割 ex_keys 为列表
            keys = ex_keys.split(",")
            # 以 , 分割 ex_values 为列表
            ex_values = getattr(case_info, 'ex_values').split(",")
            # 循环需要加入的参数字段
            for i in range(0, len(keys)):
                # 将需要加入的值以 : 分割，得到依赖的行数和取值步骤
                row_steps = ex_values[i].split(":")
                # 用对应行和取值步骤去取值
                value = self.__get_value(row_steps[0], row_steps[1])
                # 取到的值为数字类型的字符串转为 int 类型
                if isinstance(value, str) and value.isdigit():
                    value = int(value)
                # 将取出的值插入以对应的字段名插入到 params 中
                set_value(value, params, keys[i])
        # 处理完成后设置回用例对象中
        setattr(case_info, 'params', params)

    def __parse_path(self, case_info):
        """
        用于解析 path 中的占位符

        要求：
        在 ex_keys 中填写对应着 url 占位符的字段
        在 ex_values 中填写取值步骤
        """

        # 取当前用例对象的 path 字段
        path = getattr(case_info, 'path')
        # 取当前用例对象中的 params 字段
        params = getattr(case_info, 'params')
        # 正则取占位符对应的字段
        pt = re.compile(r'[{](.*?)[}]')
        keys = re.findall(pt, path)
        # 如果没有占位符直接返回
        if len(keys) == 0:
            return
        # 存在占位符则循环处理
        for key in keys:
            # 从 params 中取出占位符字段对应的值
            value = params[key]
            # 不是字符串的话将其转为字符串
            if not isinstance(value, str):
                value = str(value)
            # 将 path 中的 {key} 替换为 value
            if value:
                path = path.replace('{' + key + '}', value)
        # 处理完成后设置回用例对象中
        setattr(case_info, 'path', path)

    def __get_value(self, row, steps):
        """
        从给定行数和取值步骤，取出需要的值
        """

        # 取依赖的行数据
        ci = filter_obj_single(self.case_infos, 'id', int(row))
        # 没有取到返回 None
        if not ci:
            return None
        # 否则取出依赖行数据中的请求响应结果
        content = getattr(ci, 'response_content')
        # 有值转为字典
        if content:
            ci = json.loads(content)
        # 无值直接返回 None
        else:
            return None
        # 以给定对象和取值步骤去取出对应数据
        return get_value(ci, steps)
