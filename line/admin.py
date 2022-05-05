from django.contrib import admin
from line.models import (
    reserve_inform,reserve_search,reserve_cancel,
    userId_mapping_blockId)
# Register your models here.

class dataShow(admin.ModelAdmin):
    list_display = (
    'reserve_userId',
    'reserve_name',
    'reserve_email',
    'reserve_status',
    'reserve_time',
    'reserve_num',
    )
    
admin.site.register(reserve_inform)
admin.site.register(reserve_search)
admin.site.register(reserve_cancel)
admin.site.register(userId_mapping_blockId)