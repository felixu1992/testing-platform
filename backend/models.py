from django.core.validators import MaxLengthValidator
from django.core.validators import MinLengthValidator
from django.core.validators import MinValueValidator
from django.core.validators import EmailValidator
from django.core.validators import RegexValidator
from django.db import models


# 统一基类
class BaseEntity(models.Model):
    created_at = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='更新时间', auto_now=True)

    class Meta:
        abstract = True


# 用户
class User(BaseEntity):
    id = models.AutoField(primary_key=True)
    username = models.CharField(verbose_name='用户名', max_length=32, unique=True,
                                validators=[MinLengthValidator(1, message='最小长度为 1'),
                                            MaxLengthValidator(32, message='最大长度为 32')])
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
        ordering = ['-created_at']


# 联系人分组
class ContactorGroup(BaseEntity):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='分组名称', max_length=32,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    owner = models.IntegerField(verbose_name='分组拥有者', validators=[MinValueValidator(1, message='最小值为 1')])

    class Meta:
        # 表名
        db_table = 'platform_contactor_group'
        # 排序
        ordering = ['-created_at']
        # 唯一索引
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='contactor_group_owner_name_idx')
        ]


# 联系人
class Contactor(BaseEntity):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='联系人名称', max_length=32, unique=True,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    email = models.CharField(verbose_name='邮箱', max_length=64, unique=True,
                             validators=[MinLengthValidator(1, message='最小长度为 1'),
                                         MaxLengthValidator(64, message='最大长度为 64'),
                                         EmailValidator(message='请输入正确的邮箱账号')])
    phone = models.CharField(verbose_name='手机号', max_length=16, unique=True,
                             validators=[MinLengthValidator(1, message='最小长度为 1'),
                                         MaxLengthValidator(16, message='最大长度为 16'),
                                         RegexValidator(regex=r'^1[3,4,5,7,8]\d{9}$', message='请输入正确的手机号')])
    owner = models.IntegerField(verbose_name='项目拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    group_id = models.IntegerField(verbose_name='分组 id', default=0, validators=[MinValueValidator(1, message='最小值为 1')])

    class Meta:
        # 表名
        db_table = 'platform_contactor'
        # 排序
        ordering = ['-created_at']
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


# 文件分组
class FileGroup(BaseEntity):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='分组名称', max_length=32,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    owner = models.IntegerField(verbose_name='分组拥有者', validators=[MinValueValidator(1, message='最小值为 1')])

    class Meta:
        # 表名
        db_table = 'platform_file_group'
        # 排序
        ordering = ['-created_at']
        # 唯一索引
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='file_group_owner_name_idx')
        ]


# 文件
class File(BaseEntity):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='文件名称', max_length=32, unique=True,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    remark = models.CharField(verbose_name='文件描述', max_length=255, blank=True, null=True,
                              validators=[MaxLengthValidator(255, message='最大长度为 255')])
    owner = models.IntegerField(verbose_name='文件拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    group_id = models.IntegerField(verbose_name='分组 id', default=0, validators=[MinValueValidator(1, message='最小值为 1')])

    class Meta:
        # 表名
        db_table = 'platform_file'
        # 排序
        ordering = ['-created_at']
        # 唯一索引
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='file_owner_name_idx')
        ]
        # 普通索引
        indexes = [
            models.Index(fields=['owner', 'group_id'], name='file_owner_group_idx')
        ]


# 项目分组
class ProjectGroup(BaseEntity):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='分组名称', max_length=32,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    owner = models.IntegerField(verbose_name='分组拥有者', validators=[MinValueValidator(1, message='最小值为 1')])

    class Meta:
        # 表名
        db_table = 'platform_project_group'
        # 排序
        ordering = ['-created_at']
        # 唯一索引
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='project_group_owner_name_idx')
        ]


# 项目
class Project(BaseEntity):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='项目名称', max_length=32,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    remark = models.CharField(verbose_name='项目备注', max_length=255, default=None,
                              validators=[MaxLengthValidator(255, message='最大长度为 255')])
    cookies = models.JSONField(verbose_name='Cookie', blank=True, null=True)
    headers = models.JSONField(verbose_name='请求头', blank=True, null=True)
    host = models.CharField(verbose_name='项目统一 host', max_length=255, blank=True, null=True)
    owner = models.IntegerField(verbose_name='项目拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    group_id = models.IntegerField(verbose_name='分组 id', default=0, validators=[MinValueValidator(1, message='最小值为 1')])
    notify = models.BooleanField(verbose_name='是否发送通知', blank=True, null=True, default=True)

    class Meta:
        # 表名
        db_table = 'platform_project'
        # 排序
        ordering = ['-created_at']
        # 唯一索引
        constraints = [
            models.UniqueConstraint(fields=['owner', 'name'], name='project_owner_name_idx')
        ]
        # 普通索引
        indexes = [
            models.Index(fields=['owner', 'group_id'], name='project_owner_group_idx')
        ]


# 测试用例
class CaseInfo(BaseEntity):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='用例名称', max_length=32, unique=True,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    remark = models.CharField(verbose_name='项目备注', max_length=255, blank=True, null=True,
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
    check_step = models.TextField(verbose_name='校验步骤', blank=True, null=True)
    expected_http_status = models.IntegerField(verbose_name='Http 状态码', default=200,
                                               validators=[MinValueValidator(1, message='最小值为 1')])
    check_status = models.BooleanField(verbose_name='是否校验 Http 状态', default=False)
    run = models.BooleanField(verbose_name='是否运行', default=True)
    owner = models.IntegerField(verbose_name='拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    developer = models.IntegerField(verbose_name='接口开发者', default=0, validators=[MinValueValidator(1, message='最小值为 1')])
    notify = models.BooleanField(verbose_name='是否通知开发者', default=False)
    project_id = models.IntegerField(verbose_name='关联项目 id', validators=[MinValueValidator(1, message='最小值为 1')])
    sort = models.IntegerField(verbose_name='接口排序', default=0, validators=[MinValueValidator(1, message='最小值为 1')])

    class Meta:
        # 表名
        db_table = 'platform_case_info'
        # 排序
        ordering = ['sort', '-created_at']
        # 唯一索引
        constraints = [
            models.UniqueConstraint(fields=['owner', 'project_id', 'sort'], name='case_owner_project_sort_idx')
        ]
        # 普通索引
        indexes = [
            models.Index(fields=['owner', 'project_id', 'developer'], name='project_owner_developer_idx')
        ]


# 测试记录
class Record(BaseEntity):
    id = models.AutoField(primary_key=True)
    group_id = models.IntegerField(verbose_name='分组 id', default=0, validators=[MinValueValidator(1, message='最小值为 1')])
    project_id = models.IntegerField(verbose_name='关联项目 id', validators=[MinValueValidator(1, message='最小值为 1')])
    owner = models.IntegerField(verbose_name='拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    passed = models.IntegerField(verbose_name='通过数', default=0)
    failed = models.IntegerField(verbose_name='失败数', default=0)
    ignored = models.IntegerField(verbose_name='忽略数', default=0)
    total = models.IntegerField(verbose_name='总数', default=0)

    class Meta:
        # 表名
        db_table = 'platform_record'
        # 排序
        ordering = ['-created_at']
        # 普通索引
        indexes = [
            models.Index(fields=['owner', 'group_id'], name='record_owner_group_idx'),
            models.Index(fields=['owner', 'group_id', 'project_id'], name='record_owner_group_project_idx')
        ]


# 测试报告
class Report(BaseEntity):
    id = models.AutoField(primary_key=True)
    name = models.CharField(verbose_name='用例名称', max_length=32, unique=True,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(32, message='最大长度为 32')])
    remark = models.CharField(verbose_name='项目备注', max_length=255, default=None,
                              validators=[MinLengthValidator(1, message='最小长度为 1'),
                                          MaxLengthValidator(255, message='最大长度为 255')])
    method = models.CharField(verbose_name='请求方法', max_length=8,
                              validators=[MinLengthValidator(1, message='最小长度为 1'),
                                          MaxLengthValidator(8, message='最大长度为 8')])
    host = models.CharField(verbose_name='请求 host，没填会使用项目的', max_length=255, default=None)
    path = models.CharField(verbose_name='请求地址', max_length=255,
                            validators=[MinLengthValidator(1, message='最小长度为 1'),
                                        MaxLengthValidator(255, message='最大长度为 255')])
    params = models.JSONField(verbose_name='请求参数', blank=True, null=True)
    extend_keys = models.TextField(verbose_name='扩展字段', blank=True, null=True)
    extend_values = models.TextField(verbose_name='扩展值', blank=True, null=True)
    headers = models.JSONField(verbose_name='请求头', blank=True, null=True)
    expected_keys = models.TextField(verbose_name='预期字段', blank=True, null=True)
    expected_values = models.TextField(verbose_name='预期值', blank=True, null=True)
    check_step = models.TextField(verbose_name='校验步骤', blank=True, null=True)
    expected_http_status = models.IntegerField(verbose_name='Http 状态码', default=200,
                                               validators=[MinValueValidator(1, message='最小值为 1')])
    check_status = models.BooleanField(verbose_name='是否校验 Http 状态', default=False)
    run = models.BooleanField(verbose_name='是否运行', default=True)
    owner = models.IntegerField(verbose_name='拥有者', validators=[MinValueValidator(1, message='最小值为 1')])
    developer = models.IntegerField(verbose_name='接口开发者', default=0, validators=[MinValueValidator(1, message='最小值为 1')])
    notify = models.BooleanField(verbose_name='是否通知开发者', default=False)
    project_id = models.IntegerField(verbose_name='关联项目 id',
                                     validators=[MinValueValidator(1, message='最小值为 1')])
    sort = models.IntegerField(verbose_name='接口排序', default=0, validators=[MinValueValidator(1, message='最小值为 1')])
    status = models.CharField(verbose_name='执行状态', max_length=8,
                              validators=[MinLengthValidator(1, message='最小长度为 1'),
                                          MaxLengthValidator(8, message='最大长度为 8')])
    response_code = models.CharField(verbose_name='响应状态', max_length=8, blank=True, null=True,
                                     validators=[MinLengthValidator(1, message='最小长度为 1'),
                                                 MaxLengthValidator(8, message='最大长度为 8')])
    http_status = models.IntegerField(verbose_name='Http 状态码', default=200,
                                      validators=[MinValueValidator(1, message='最小值为 1')])
    response_content = models.TextField(verbose_name='响应状态', blank=True, null=True)
    time_used = models.IntegerField(verbose_name='请求耗时', default=0)
    record_id = models.IntegerField(verbose_name='记录 id', validators=[MinValueValidator(1, message='最小值为 1')])

    class Meta:
        # 表名
        db_table = 'platform_report'
        # 排序
        ordering = ['-created_at']
        # 普通索引
        indexes = [
            models.Index(fields=['owner', 'record_id'], name='report_owner_record_idx')
        ]
