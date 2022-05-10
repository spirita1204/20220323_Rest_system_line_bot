from distutils.text_file import TextFile
from django.db import models
import django.utils.timezone as timezone

# Create your models here.
class reserve_inform(models.Model):
    reserve_userId = models.TextField(default="",null=True, blank=True)
    reserve_name = models.TextField(default="",null=True, blank=True)
    reserve_email = models.TextField(default="",null=True, blank=True)
    reserve_status = models.TextField(default="初始狀態")
    reserve_datetime = models.DateTimeField('預訂日期',default = timezone.now)  
    
    reserve_name_confirm = models.TextField(default="",null=True, blank=True)
    reserve_email_confirm = models.TextField(default="",null=True, blank=True)
    reserve_datetime_confirm = models.DateTimeField('預訂日期確認',default = timezone.now)  
    

class reserve_search(models.Model):
    reserve_search_userId = models.TextField(default="")
    reserve_search_name = models.TextField(default="")
    reserve_search_email = models.TextField(default="")
    reserve_search_status = models.TextField(default="搜尋_初始狀態")

class reserve_cancel(models.Model):
    reserve_cancel_userId = models.TextField(default="")
    reserve_cancel_name = models.TextField(default="")
    reserve_cancel_email = models.TextField(default="")
    reserve_cancel_status = models.TextField(default="取消_初始狀態")

class userId_mapping_blockId (models.Model):
    userId = models.TextField(default="")
    blockId = models.TextField(default="")