from django.db import models

# Create your models here.
class Details(models.Model):
    username = models.CharField(max_length=56)