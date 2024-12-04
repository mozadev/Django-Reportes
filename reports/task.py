from celery import shared_task
from datetime import datetime, timedelta
from .services import FastAPIClient
from .models import ExcelReport
from django.core.files.base import ContentFile

@shared_task
async def fetch_daily_reports():
    """Fetch previous day's reports at 5 AM"""
    yesterday = datetime.now() - timedelta(days=1)
    client = FastAPIClient()

    try:
        if not ExcelReport.objects.filter(report_date=yesterday.date()).exists():
            file_content, content_type = await client.fetch_excel_report(yesterday)
            filename = f"report_{yesterday.strftime('%Y-%m-%d')}.xlsx"
            
            report = ExcelReport(report_date=yesterday.date())
            report.file.save(filename, ContentFile(file_content), save=True)
            report.status = 'downloaded'
            report.save()
            
    except Exception as e:
        logger.error(f"Error in daily report fetch: {str(e)}")