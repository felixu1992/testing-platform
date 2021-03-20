from rest_framework import serializers, viewsets

from backend.models import Role
from backend.util import parse_data, save, Response, next_id


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'role', 'remark', 'created_at', 'updated_at']


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Role.objects

    serializer_class = RoleSerializer

    def create(self, request, *args, **kwargs):
        """
        创建角色
        """

        body = parse_data(request, 'POST')
        role = Role(**body)
        role.id = next_id()
        save(role)
        return Response.success(role)
