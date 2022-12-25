from django.db import models


# Create your models here.
class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    permission_rank = models.IntegerField()
    user_name = models.CharField(max_length=32, unique=True)
    password = models.CharField(default=None, max_length=128)
    available_store = models.FloatField(max_length=16)
    max_store = models.FloatField(max_length=16)
    user_avatar = models.ImageField(null=True, blank=True)
    user_tele = models.CharField(max_length=11)
    user_birth = models.DateField()
    last_login = models.DateTimeField(auto_now=True)
