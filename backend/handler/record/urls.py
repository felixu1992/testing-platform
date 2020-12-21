from rest_framework import routers
from backend.handler.record import report, record

# 用例记录
record_router = routers.DefaultRouter()
record_router.register(r'', record.RecordViewSet, basename='record')
# 用例报告
report_router = routers.DefaultRouter()
report_router.register(r'', report.ReportViewSet, basename='report')
