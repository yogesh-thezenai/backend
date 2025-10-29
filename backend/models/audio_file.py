from django.db import models


class AudioFile(models.Model):
    id = models.AutoField(primary_key=True, )
    file_path = models.CharField(max_length=255)
    language = models.CharField(max_length=50)
    process_name = models.CharField(max_length=100)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_url = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.process_name} - {self.language}"
