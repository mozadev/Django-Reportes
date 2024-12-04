from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExcelReportViewSet

router = DefaultRouter()
router.register(r'reports', ExcelReportViewSet, basename='report')

urlpatterns = [
    path('', include(router.urls)),
]