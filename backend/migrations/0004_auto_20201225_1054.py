# Generated by Django 3.1.2 on 2020-12-25 02:54

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_auto_20201224_1116'),
    ]

    operations = [
        migrations.AddField(
            model_name='caseinfo',
            name='delay',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0, message='最小值为 0'), django.core.validators.MaxValueValidator(300, message='最大值为 300')], verbose_name='延迟执行时长, 单位秒, 最长延时五分钟即 300'),
        ),
        migrations.AddField(
            model_name='caseinfo',
            name='sample',
            field=models.JSONField(blank=True, null=True, verbose_name='结果示例，用于接口依赖时方便直接获得取值步骤'),
        ),
        migrations.AlterField(
            model_name='file',
            name='name',
            field=models.CharField(max_length=32, validators=[django.core.validators.MinLengthValidator(1, message='最小长度为 1'), django.core.validators.MaxLengthValidator(32, message='最大长度为 32')], verbose_name='文件名称'),
        ),
        migrations.AlterField(
            model_name='project',
            name='notify',
            field=models.BooleanField(blank=True, default=False, null=True, verbose_name='是否发送通知'),
        ),
    ]
