# Generated by Django 3.1.2 on 2020-11-20 04:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='role',
            field=models.CharField(default='ROLE_ADMIN', max_length=16, validators=[django.core.validators.MinLengthValidator(1, message='最小长度为 1'), django.core.validators.MaxLengthValidator(32, message='最大长度为 16')], verbose_name='角色'),
            preserve_default=False,
        ),
    ]
