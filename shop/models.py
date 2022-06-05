from django.db import models

# Create your models here.
class order_info(models.Model):
    # 購買者姓名
    order_name = models.TextField(default="",null=True, blank=True)
    # 購買者信箱
    order_email = models.TextField(default="",null=True, blank=True)
    # 購買者位址
    order_address = models.TextField(default="",null=True, blank=True)
    # 購買品項
    order_item = models.TextField(default="",null=True, blank=True)
    # 購買金額
    order_price = models.TextField(default="",null=True, blank=True)
    # 訂單是否成立
    is_valid = models.BooleanField(default=False)
