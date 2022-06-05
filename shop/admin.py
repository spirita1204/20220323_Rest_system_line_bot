from django.contrib import admin

# Register your models here.
from shop.models import (
   order_info)
# Register your models here.

class dataShow(admin.ModelAdmin):
    list_display = (
 
    )
    
admin.site.register(order_info)