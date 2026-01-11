from django.db import models
from beskidscore import settings
from data.models import CSVLeagueFilesM


class ProcessedTasksM(models.Model):
    task_name = models.CharField(max_length=100)
    STATUS_CHOICES = (
        ('NEW', 'NEW'),
        ('IN_PROGRESS', 'IN_PROGRESS'),
        ('COMPLETED', 'COMPLETED'),
        ('FAILED', 'FAILED'),
    )
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default='NEW')
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    more_info = models.TextField(blank=True, null=True)
    file_id = models.ForeignKey(CSVLeagueFilesM, on_delete=models.CASCADE)
    error_name = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)