from django.db import models


# Create your models here.
class Share(models.Model):
    share_id = models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=32, unique=True)
    share_password = models.CharField(default=None, max_length=128)
    deadline = models.DateTimeField()
    file_size = models.FloatField(max_length=16)
    file_path = models.CharField(max_length=32)
