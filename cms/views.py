from django.shortcuts import render,redirect
from line.models import reserve_inform
from datetime import datetime

#瀏覽訂位資訊
def reserve_detail(request):
    #取出時間大於當前的資料供cms檢視
    #__lte, __gte, __lt, __gt are used for <=, >=, < and >
    reserve_details = reserve_inform.objects.filter(reserve_datetime_confirm__lte=datetime.now())
    context = {
        'dateTimeNow':datetime.now(),
        'reserve_details':reserve_details
    }
    return render(request, "cms/cms.html",context)

def delete(request,pk): #刪除資料 ,pk傳哪張
    if request.method == "POST":
        reserve_details = reserve_inform.objects.get(pk=pk)
        reserve_details.delete()
    return redirect('/cms/reserve_detail/')