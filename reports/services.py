import httpx
from datetime import datetime, timedelta
from django.conf import settings
import asyncio
from asgiref.sync import sync_to_async
import logging

logger = logging.getLogger(__name__)

class FastAPIClient:
    def __init__(self):
        self.base_url = settings.FASTAPI_BASE_URL
        self.timeout = httpx.Timeout(30.0)

    async def fetch_excel_report(self, start_date: datetime, end_date: datetime = None):
        """Fetch Excel report from FastAPI"""
        try:
            params = {
                'start_date': start_date.strftime('%Y-%m-%d'),
                'end_date': end_date.strftime('%Y-%m-%d') if end_date else None
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/sga/reporte",
                    json=params
                )
                response.raise_for_status()
                return response.content, response.headers.get('content-type')
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error occurred: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error fetching report: {str(e)}")
            raise