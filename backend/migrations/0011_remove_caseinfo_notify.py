# Generated by Django 3.1.2 on 2021-01-26 19:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0010_auto_20210120_2223'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='caseinfo',
            name='notify',
        ),
    ]
