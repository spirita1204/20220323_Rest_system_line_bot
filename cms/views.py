from django.shortcuts import render,redirect
from line.models import reserve_inform
from datetime import datetime
from .forms import DatetimeModelForm
#瀏覽訂位資訊
def reserve_detail(request):
    datetimeForm = DatetimeModelForm()
    
    #update modal修改相對cms為post,進來再處理
    if request.method == "POST":
        print("entry")
        form = DatetimeModelForm(request.POST)
        form_name = form["reserve_name_confirm"].value()
        
        if form.is_valid():
            pass
            #reserve_inform.objects.get(pk=pk) 
        return redirect("/cms/reserve_detail/")

    #取出時間大於當前的資料供cms檢視
    #__lte, __gte, __lt, __gt are used for <=, >=, < and >
    reserve_details = reserve_inform.objects.filter(reserve_datetime_confirm__lte=datetime.now())
    context = {
        'dateTimeNow':datetime.now(),
        'reserve_details':reserve_details,
        'datetimeForm':datetimeForm
    }
    return render(request, "cms/cms.html",context)

def delete(request,pk): #刪除資料 ,pk傳哪個 
    if request.method == "POST":
        reserve_details = reserve_inform.objects.get(pk=pk)
        reserve_details.delete()
    return redirect('/cms/reserve_detail/')

def update(request,pk): #修改資料 ,pk傳哪個 
    print("update start!")
    
    if request.method == "POST":
        reserve_details = reserve_inform.objects.get(pk=pk) 
    print("update")    
    return redirect('/cms/reserve_detail/')
