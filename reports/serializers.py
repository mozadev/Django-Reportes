from rest_framework import serializers
from .models import ExcelReport

class ExcelReportSerializer(serializers.ModelSerializer):
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = ExcelReport
        fields = ['id', 'report_date', 'status', 'created_at', 'download_url', 'error_message']
        read_only_fields = ['created_at', 'status', 'error_message']

    def get_download_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            return request.build_absolute_uri(obj.file.url)
        return None