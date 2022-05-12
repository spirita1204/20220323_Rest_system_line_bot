from django.shortcuts import render, redirect
from line.models import reserve_inform, reserve_search
from datetime import datetime
from .forms import DatetimeModelForm
# 瀏覽訂位資訊


def reserve_detail(request):
    datetimeForm = DatetimeModelForm()

    # update modal修改相對cms為post,進來再處理
    if request.method == "POST":
        print("entry")
        return redirect("/cms/reserve_detail/")

    # 取出時間大於當前的資料供cms檢視
    # __lte, __gte, __lt, __gt are used for <=, >=, < and >
    reserve_details = reserve_inform.objects.filter(
        reserve_datetime_confirm__gte=datetime.now())
    context = {
        'dateTimeNow': datetime.now(),#比較用
        'reserve_details': reserve_details,
        'datetimeForm': datetimeForm
    }
    return render(request, "cms/cms.html", context)


def delete(request, pk):  # 刪除資料 ,pk傳哪個
    print(pk)
    if request.method == "POST":
        reserve_details = reserve_inform.objects.get(pk=pk)
        reserve_details.delete()
    return redirect('/cms/reserve_detail/')


def update(request, pk):  # 修改資料 ,pk傳哪個
    print(pk)
    reserve_details = reserve_inform.objects.get(pk=pk)

    if request.method == "POST":
        form = DatetimeModelForm(request.POST, instance=reserve_details)
        if form.is_valid():
            form_name = form["reserve_name_confirm"].value()
            form_email = form["reserve_email_confirm"].value()
            form_datetime = form["reserve_datetime_confirm"].value()
            #存入指定pk資料
            form.reserve_name_confirm = form_name
            form.reserve_email_confirm = form_email
            form.reserve_datetime_confirm = form_datetime
            form.save()
            print("form update!")
    return redirect('/cms/reserve_detail/')
