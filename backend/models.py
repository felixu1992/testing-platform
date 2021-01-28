from django.core.validators import MaxLengthValidator, MaxValueValidator
from django.core.validators import MinLengthValidator
from django.core.validators import MinValueValidator
from django.core.validators import EmailValidator
from django.core.validators import RegexValidator
from django.db import models
from django.db.models import QuerySet
from django.db.models.manager import BaseManager
from backend.exception import ErrorCode, ValidateError


class PlatformQuerySet(QuerySet):
    """
    对原生 QuerySet 做一层封装，使其更加方便进行模糊查询、精确匹配等操作
    """

    def owner(self):
        from backend.util import UserHolder
        return self.filter(owner=UserHolder.current_user())

    def contains(self, **kwargs):
        """
        所有字段模糊查询
        """

        return self.__update(operation='__contains', **kwargs)

    def exact(self, **kwargs):
        """
        所有字段精确匹配
        """

        return self.__update(operation='__exact', **kwargs)

    def iexact(self, **kwargs):
        """
        所有字段忽略大小写精确匹配
        """

        return self.__update(operation='__iexact', **kwargs)

    def fields_in(self, **kwargs):
        """
        In 查询
        """

        return self.__update(operation='__in', **kwargs)

    def lt(self, e=False, **kwargs):
        """
        小于 / 小于等于
        """

        if e:
            return self.__update(operation='__lte', **kwargs)
        return self.__update(operation='__lt', **kwargs)

    def gt(self, e=False, **kwargs):
        """
        大于 / 大于等于
        """

        if e:
            return self.__update(operation='__gte', **kwargs)
        return self.__update(operation='__gt', **kwargs)

    def __update(self, operation, **kwargs):
        """
        对字典进行更新
        """

        if kwargs is None:
            raise ValidateError.error(ErrorCode.MISSING_NECESSARY_KEY, 'kwargs')
        query_dict = {}
        for key, value in kwargs.items():
            if value:
                # 拼上 QuerySet 字段属性
                query_dict.update({key + operation: value})
        return self.filter(**query_dict)


class PlatformManager(BaseManager.from_queryset(PlatformQuerySet)):
    """
    实现 Model 中的 Manager

    与官网不同的是:
    我没有继承他的 Manager 添加方法，因为官网的方式只能在 Entity.objects.xxx 来使用自己 Manager 中的方法
    而是参照 models。Manager 的实现，将 QuerySet 替换为我的 PlatformQuerySet
    这样的好处是，不论在链式调用中的什么环节，均可以链式嵌入自己的封装方法
    """
    pass


class BaseEntity(models.Model):
    """
    统一基类
    """

    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)
    objects = PlatformManager()

    class Meta:
        abstract = True


class User(BaseEntity):
    """
    用户
    """

    id = models.AutoField(primary_key=True)
    username = models.CharField(verbose_name='用户名', max_length=32, unique=True,
                                validators=[MinLengthValidator(1, message='最小长度为 1'),
                                            MaxLengthValidator(32, message='最大长度为 32')])
    role = models.CharField(verbose_name='角色', max_length=16,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 16')])
    email = models.CharField(verbose_name='邮箱', max_length=64, unique=True,
                             validators=[MinLengthValidator(1, message='最小长度为 1'),
                                         MaxLengthValidator(64, message='最大长度为 64'),
                                         EmailValidator(message='请输入正确的邮箱账号')])
    phone = models.CharField(verbose_name='手机号', max_length=16, unique=True,
                             validators=[MinLengthValidator(1, message='最小长度为 1'),
                                         MaxLengthValidator(16, message='最大长度为 16'),
                                         RegexValidator(regex=r'^1[3,4,5,7,8]\d{9}$', message='请输入正确的手机号')])
    password = models.CharField(verbose_name='密码', max_length=128,
                                validators=[MinLengthValidator(1, message='最小长度为 1'),
                                            MaxLengthValidator(16, message='最大长度为 16')])
    avatar = models.CharField(verbose_name='头像', max_length=255, blank=True, null=True)

    class Meta:
        # 表名
        db_table = 'platform_user'
        # 排序
        ordering = ['-updated_at']


class ContactorGroup(BaseEntity):
    """
    联系人分组
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='分组名称', max_length=32,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    owner = models.IntegerField(verbose_name='分组拥有者', validators=[MinValueValidator(1, message='最小值为 1')])

    class Meta:
        # 表名
        db_table = 'platform_contactor_group'
        # 排序
        ordering = ['-updated_at']
        # 唯一索引
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='contactor_group_owner_name_idx')
        ]


class Contactor(BaseEntity):
    """
    联系人
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='联系人名称', max_length=32,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    email = models.CharField(verbose_name='邮箱', max_length=64,
                             validators=[MinLengthValidator(1, message='最小长度为 1'),
                                         MaxLengthValidator(64, message='最大长度为 64'),
                                         EmailValidator(message='请输入正确的邮箱账号')])
    phone = models.CharField(verbose_name='手机号', max_length=16,
                             validators=[MinLengthValidator(1, message='最小长度为 1'),
                                         MaxLengthValidator(16, message='最大长度为 16'),
                                         RegexValidator(regex=r'^1[3,4,5,7,8]\d{9}$', message='请输入正确的手机号')])
    owner = models.IntegerField(verbose_name='项目拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    group_id = models.IntegerField(verbose_name='分组 id', default=0, validators=[MinValueValidator(1, message='最小值为 1')])

    class Meta:
        # 表名
        db_table = 'platform_contactor'
        # 排序
        ordering = ['-updated_at']
        # 唯一索引
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='contactor_owner_name_idx'),
            models.UniqueConstraint(fields=['owner', 'email'], name='contactor_owner_email_idx'),
            models.UniqueConstraint(fields=['owner', 'phone'], name='contactor_owner_phone_idx'),
        ]
        # 普通索引
        indexes = [
            models.Index(fields=['owner', 'group_id'], name='contactor_owner_group_idx')
        ]


class FileGroup(BaseEntity):
    """
    文件分组
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='分组名称', max_length=32,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    owner = models.IntegerField(verbose_name='分组拥有者', validators=[MinValueValidator(1, message='最小值为 1')])

    class Meta:
        # 表名
        db_table = 'platform_file_group'
        # 排序
        ordering = ['-updated_at']
        # 唯一索引
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='file_group_owner_name_idx')
        ]


class File(BaseEntity):
    """
    文件
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='文件名称', max_length=32,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    path = models.CharField(verbose_name='文件路径', max_length=255,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(255, message='最大长度为 255')])
    remark = models.CharField(verbose_name='文件描述', max_length=255, blank=True, null=True,
                              validators=[MaxLengthValidator(255, message='最大长度为 255')])
    owner = models.IntegerField(verbose_name='文件拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    group_id = models.IntegerField(verbose_name='分组 id', default=0, validators=[MinValueValidator(1, message='最小值为 1')])

    class Meta:
        # 表名
        db_table = 'platform_file'
        # 排序
        ordering = ['-updated_at']
        # 唯一索引
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='file_owner_name_idx')
        ]
        # 普通索引
        indexes = [
            models.Index(fields=['owner', 'group_id'], name='file_owner_group_idx')
        ]


class ProjectGroup(BaseEntity):
    """
    项目分组
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='分组名称', max_length=32,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    owner = models.IntegerField(verbose_name='分组拥有者', validators=[MinValueValidator(1, message='最小值为 1')])

    class Meta:
        # 表名
        db_table = 'platform_project_group'
        # 排序
        ordering = ['-updated_at']
        # 唯一索引
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='project_group_owner_name_idx')
        ]


class Project(BaseEntity):
    """
    项目
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='项目名称', max_length=32,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    remark = models.CharField(verbose_name='项目备注', max_length=255, default=None,
                              validators=[MaxLengthValidator(255, message='最大长度为 255')])
    headers = models.JSONField(verbose_name='请求头', blank=True, null=True)
    host = models.CharField(verbose_name='项目统一 host', max_length=255, blank=True, null=True)
    owner = models.IntegerField(verbose_name='项目拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    group_id = models.IntegerField(verbose_name='分组 id', default=0, validators=[MinValueValidator(1, message='最小值为 1')])
    notify = models.BooleanField(verbose_name='是否发送通知', blank=True, null=True, default=False)

    class Meta:
        # 表名
        db_table = 'platform_project'
        # 排序
        ordering = ['-updated_at']
        # 唯一索引
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='project_owner_name_idx')
        ]
        # 普通索引
        indexes = [
            models.Index(fields=['owner', 'group_id'], name='project_owner_group_idx')
        ]


class CaseInfo(BaseEntity):
    """
    测试用例
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='用例名称', max_length=32,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    remark = models.CharField(verbose_name='用例备注', max_length=255, blank=True, null=True,
                              validators=[MinLengthValidator(1, message='最小长度为 1'),
                                          MaxLengthValidator(255, message='最大长度为 255')])
    method = models.CharField(verbose_name='请求方法', max_length=8,
                              validators=[MinLengthValidator(1, message='最小长度为 1'),
                                          MaxLengthValidator(8, message='最大长度为 8')])
    host = models.CharField(verbose_name='请求 host，没填会使用项目的', max_length=255, blank=True, null=True)
    path = models.CharField(verbose_name='请求地址', max_length=255,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(255, message='最大长度为 255')])
    headers = models.JSONField(verbose_name='请求头', blank=True, null=True)
    run = models.BooleanField(verbose_name='是否运行', default=True)
    check_status = models.BooleanField(verbose_name='是否校验 Http 状态', default=False)
    project_id = models.IntegerField(verbose_name='关联项目 id', validators=[MinValueValidator(1, message='最小值为 1')])
    developer = models.IntegerField(verbose_name='接口开发者', blank=True, null=True)
    sort = models.IntegerField(verbose_name='接口排序', default=0, validators=[MinValueValidator(1, message='最小值为 1')])
    delay = models.IntegerField(verbose_name='延迟执行时长, 单位秒, 最长延时五分钟即 300', default=0,
                                validators=[MinValueValidator(0, message='最小值为 0'),
                                            MaxValueValidator(300, message='最大值为 300')])
    expected_http_status = models.IntegerField(verbose_name='Http 状态码', blank=True, null=True, default=200,
                                               validators=[MinValueValidator(1, message='最小值为 1')])
    owner = models.IntegerField(verbose_name='拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    params = models.JSONField(verbose_name='请求参数', blank=True, null=True)
    sample = models.JSONField(verbose_name='结果示例，用于接口依赖时方便直接获得取值步骤', blank=True, null=True)

    extend_keys = models.TextField(verbose_name='扩展字段', blank=True, null=True)
    extend_values = models.TextField(verbose_name='扩展值', blank=True, null=True)
    expected_keys = models.TextField(verbose_name='预期字段', blank=True, null=True)
    expected_values = models.TextField(verbose_name='预期值', blank=True, null=True)

    class Meta:
        # 表名
        db_table = 'platform_case_info'
        # 排序
        ordering = ['sort', '-updated_at']
        # 普通索引
        indexes = [
            models.Index(fields=['owner', 'project_id', 'developer'], name='project_owner_developer_idx')
        ]


class Record(BaseEntity):
    """
    测试记录
    """

    id = models.AutoField(primary_key=True)
    group_id = models.IntegerField(verbose_name='分组 id', default=0, validators=[MinValueValidator(1, message='最小值为 1')])
    project_id = models.IntegerField(verbose_name='关联项目 id', validators=[MinValueValidator(1, message='最小值为 1')])
    remark = models.CharField(verbose_name='记录描述', max_length=255, default=None, blank=True, null=True,
                              validators=[MinLengthValidator(1, message='最小长度为 1'),
                                          MaxLengthValidator(255, message='最大长度为 255')])
    owner = models.IntegerField(verbose_name='拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    passed = models.IntegerField(verbose_name='通过数', default=0)
    failed = models.IntegerField(verbose_name='失败数', default=0)
    ignored = models.IntegerField(verbose_name='忽略数', default=0)
    total = models.IntegerField(verbose_name='总数', default=0)

    class Meta:
        # 表名
        db_table = 'platform_record'
        # 排序
        ordering = ['-updated_at']
        # 普通索引
        indexes = [
            models.Index(fields=['owner', 'group_id'], name='record_owner_group_idx'),
            models.Index(fields=['owner', 'group_id', 'project_id'], name='record_owner_group_project_idx')
        ]


class Report(BaseEntity):
    """
    测试报告
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='用例名称', max_length=32,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    remark = models.CharField(verbose_name='用例备注', max_length=255, blank=True, null=True,
                              validators=[MinLengthValidator(1, message='最小长度为 1'),
                                          MaxLengthValidator(255, message='最大长度为 255')])
    method = models.CharField(verbose_name='请求方法', max_length=8,
                              validators=[MinLengthValidator(1, message='最小长度为 1'),
                                          MaxLengthValidator(8, message='最大长度为 8')])
    host = models.CharField(verbose_name='请求 host，没填会使用项目的', max_length=255, blank=True, null=True)
    path = models.CharField(verbose_name='请求地址', max_length=255,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(255, message='最大长度为 255')])
    params = models.JSONField(verbose_name='请求参数', blank=True, null=True)
    extend_keys = models.TextField(verbose_name='扩展字段', blank=True, null=True)
    extend_values = models.TextField(verbose_name='扩展值', blank=True, null=True)
    headers = models.JSONField(verbose_name='请求头', blank=True, null=True)
    expected_keys = models.TextField(verbose_name='预期字段', blank=True, null=True)
    expected_values = models.TextField(verbose_name='预期值', blank=True, null=True)
    expected_http_status = models.IntegerField(verbose_name='Http 状态码', blank=True, null=True, default=200,
                                               validators=[MinValueValidator(1, message='最小值为 1')])
    check_status = models.BooleanField(verbose_name='是否校验 Http 状态', default=False)
    run = models.BooleanField(verbose_name='是否运行', default=True)
    owner = models.IntegerField(verbose_name='拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    developer = models.IntegerField(verbose_name='接口开发者', blank=True, null=True)
    project_id = models.IntegerField(verbose_name='关联项目 id', validators=[MinValueValidator(1, message='最小值为 1')])
    sort = models.IntegerField(verbose_name='接口排序', default=0, validators=[MinValueValidator(1, message='最小值为 1')])
    delay = models.IntegerField(verbose_name='延迟执行时长, 单位秒, 最长延时五分钟即 300', default=0,
                                validators=[MinValueValidator(0, message='最小值为 0'),
                                            MaxValueValidator(300, message='最大值为 300')])
    sample = models.JSONField(verbose_name='结果示例，用于接口依赖时方便直接获得取值步骤', blank=True, null=True)
    case_id = models.IntegerField(verbose_name='等同于用例 id', default=0,
                                  validators=[MinValueValidator(1, message='最小值为 1')])
    response_code = models.CharField(verbose_name='响应状态', max_length=8, blank=True, null=True,
                                     validators=[MinLengthValidator(1, message='最小长度为 1'),
                                                 MaxLengthValidator(8, message='最大长度为 8')])
    http_status = models.IntegerField(verbose_name='Http 状态码', default=200,
                                      validators=[MinValueValidator(1, message='最小值为 1')])
    response_content = models.JSONField(verbose_name='响应状态', blank=True, null=True)
    time_used = models.IntegerField(verbose_name='请求耗时', default=0)
    record_id = models.IntegerField(verbose_name='记录 id', validators=[MinValueValidator(1, message='最小值为 1')])
    status = models.CharField(verbose_name='用例执行结果', max_length=8, default='FAILED',
                              validators=[MinLengthValidator(1, message='最小长度为 1'),
                                          MaxLengthValidator(8, message='最大长度为 8')])

    class Meta:
        # 表名
        db_table = 'platform_report'
        # 排序
        ordering = ['sort', '-updated_at']
        # 普通索引
        indexes = [
            models.Index(fields=['owner', 'record_id'], name='report_owner_record_idx')
        ]
