# Generated by Django 3.1.2 on 2020-12-26 13:43

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0007_auto_20201225_1630'),
    ]

    operations = [
        migrations.AlterField(
            model_name='record',
            name='remark',
            field=models.CharField(blank=True, default=None, max_length=255, null=True, validators=[django.core.validators.MinLengthValidator(1, message='最小长度为 1'), django.core.validators.MaxLengthValidator(255, message='最大长度为 255')], verbose_name='记录描述'),
        ),
    ]
