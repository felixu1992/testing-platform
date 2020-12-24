import os
import time
from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.http import FileResponse
from django.utils.http import urlquote
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from backend import FILE_REPO
from backend.exception import ErrorCode, ValidateError, PlatformError
from backend.models import File
from backend.handler.file import file_group
from backend.util import Response, parse_data, get_params, update_fields, page_params, save


class FileSerializer(serializers.ModelSerializer):
    class Meta:
        model = File
        fields = ['id', 'name', 'path', 'remark', 'group_id', 'created_at', 'updated_at']


class FileViewSet(viewsets.ModelViewSet):
    queryset = File.objects

    serializer_class = FileSerializer

    def create(self, request, *args, **kwargs):
        """
        创建文件
        """

        body = parse_data(request, 'POST')
        file = File(**body)
        # 校验分组是否存在
        file_group.get_by_id(file.group_id)
        # 处理文件
        file.path = _file_data(request)
        save(file)
        return Response.success(file)

    def destroy(self, request, *args, **kwargs):
        """
        根据 id 删除文件
        """

        parse_data(request, 'DELETE')
        id = kwargs['pk']
        file = get_by_id(id)
        # TODO 判断是否被用例使用
        # 删除文件
        if os.path.exists(file.path):
            os.remove(file.path)
        file.delete()
        return Response.def_success()

    def update(self, request, *args, **kwargs):
        """
        修改联系人
        """

        data = parse_data(request, 'PUT')
        id, name, remark = get_params(data, 'id', 'name', 'remark', toleration=True).values()
        file = get_by_id(id)
        # 校验分组是否存在
        file_group.get_by_id(file.group_id)
        # 处理文件
        path = _file_data(request, toleration=True)
        update_fields(file, name=name, remark=remark, path=path)
        save(file)
        return Response.success(file)

    def list(self, request, *args, **kwargs):
        """
        分页查询文件列表
        可全量分页(当然只有自己的数据)
        可传入分组
        可传入 name 模糊
        """

        data = parse_data(request, 'GET')
        page, page_size, name = page_params(data, 'name').values()
        files = File.objects.owner().contains(name=name)
        page_files = Paginator(files, page_size)
        result = page_files.page(page)
        # 得到所有分组 id
        group_ids = [o.group_id for o in result.object_list]
        group_names = {}
        groups = file_group.get_list_by_ids(group_ids)
        for group in groups:
            group_names.update({group.id: group.name})
        for file in result.object_list:
            group_name = group_names[file.group_id]
            if group_name:
                file.group_name = group_name
        return Response.success(result)

    @action(methods=['GET'], detail=True)
    def download(self, request, pk):
        """
        下载文件
        """

        parse_data(request, 'GET')
        file = get_by_id(pk)
        path = file.path
        file = open(path, 'rb')
        response = FileResponse(file)
        ps = path.split('.')
        suffix = ps[len(ps) - 1]
        response['Content-Disposition'] = 'attachment;filename="%s"' % urlquote(file.name + '.' + suffix)
        return response


# -------------------------------------------- 以上为 RESTFUL 接口，以下为调用接口 -----------------------------------------

def get_by_id(id):
    """
    根据 id 查询文件信息
    """

    try:
        file = File.objects.owner().get(id=id)
    except ObjectDoesNotExist:
        raise PlatformError.error(ErrorCode.DATA_NOT_EXISTED)
    return file


def count_by_group(group_id):
    """
    根据分组 id 计数
    """

    return File.objects.owner().filter(group_id=group_id).count()


def _file_data(request, toleration=False):
    # 获得所有文件
    files = request.FILES.getlist('files')
    if toleration and len(files) == 0:
        return None
    if len(files) == 0 or len(files) > 1:
        raise ValidateError.error(ErrorCode.VALIDATION_ERROR, '请检查文件数目，需要有且仅有一个文件')
    file = files[0]
    file_path = os.path.join(FILE_REPO, str(int(time.time() * 1000)) + file.name)
    # 写文件
    dest = open(file_path, 'wb+')
    for chunk in file.chunks():
        dest.write(chunk)
    dest.close()
    # 返回文件路径
    return file_path
