from django.shortcuts import render

# Create your views here.


from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime, timedelta
from .models import ExcelReport
from .serializers import ExcelReportSerializer
from .services import FastAPIClient
from django.core.files.base import ContentFile
import asyncio

class ExcelReportViewSet(viewsets.ViewSet):
    def list(self, request):
        queryset = ExcelReport.objects.all()
        serializer = ExcelReportSerializer(
            queryset, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        try:
            report = ExcelReport.objects.get(pk=pk)
            serializer = ExcelReportSerializer(
                report,
                context={'request': request}
            )
            return Response(serializer.data)
        except ExcelReport.DoesNotExist:
            return Response(
                {"detail": "Report not found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['post'])
    async def fetch_reports(self, request):
        try:
            # Validate dates
            start_date = request.data.get('start_date')
            end_date = request.data.get('end_date')

            if not start_date:
                start_date = (timezone.now() - timedelta(days=1)).date()
            else:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            else:
                end_date = start_date

            # Initialize FastAPI client
            client = FastAPIClient()

            # Fetch and save reports
            missing_dates = []
            current_date = start_date
            while current_date <= end_date:
                if not await self._report_exists(current_date):
                    missing_dates.append(current_date)
                current_date += timedelta(days=1)

            for date in missing_dates:
                try:
                    file_content, content_type = await client.fetch_excel_report(date)
                    await self._save_report(date, file_content)
                except Exception as e:
                    logger.error(f"Error fetching report for {date}: {str(e)}")

            return Response({
                "message": f"Processed reports from {start_date} to {end_date}",
                "processed_dates": len(missing_dates)
            })

        except Exception as e:
            logger.error(f"Error in fetch_reports: {str(e)}")
            return Response(
                {"detail": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    async def _report_exists(self, date):
        try:
            return await sync_to_async(ExcelReport.objects.filter(report_date=date).exists)()
        except Exception:
            return False

    async def _save_report(self, date, content):
        try:
            filename = f"report_{date.strftime('%Y-%m-%d')}.xlsx"
            report = ExcelReport(report_date=date)
            report.file.save(filename, ContentFile(content), save=True)
            report.status = 'downloaded'
            await sync_to_async(report.save)()
        except Exception as e:
            logger.error(f"Error saving report: {str(e)}")
            raise