from django.db import models

class oper_para(models.Model):
    name = models.CharField(max_length=20)
    content = models.CharField(max_length=200)

# Create your models here.
