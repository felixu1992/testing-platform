# Generated by Django 3.1.2 on 2021-01-20 22:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0009_auto_20210115_1738'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='caseinfo',
            name='case_owner_project_sort_idx',
        ),
    ]
