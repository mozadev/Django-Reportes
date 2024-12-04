from django.db import models
from django.core.validators import FileExtensionValidator

class ExcelReport(models.Model):
    file = models.FileField(
        upload_to='excels/%Y/%m/%d/',
        validators=[FileExtensionValidator(['xlsx'])]
    )
    report_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('downloaded', 'Downloaded'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    error_message = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-report_date']
        unique_together = ['report_date']
        indexes = [
            models.Index(fields=['report_date']),
            models.Index(fields=['status'])
        ]

    def __str__(self):
        return f"Report for {self.report_date}"