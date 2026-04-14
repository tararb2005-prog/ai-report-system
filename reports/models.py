from django.db import models
from django.contrib.auth.models import User

class Report(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file_name = models.CharField(max_length=255)
    pdf_file = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.file_name