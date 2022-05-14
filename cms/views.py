from django.shortcuts import render, redirect
from line.models import reserve_inform, reserve_search
from datetime import datetime
from .forms import DatetimeModelForm
# 登入用
from django.contrib import auth
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth import logout as django_logout
from django.contrib.auth.decorators import login_required
#輸出登入錯誤訊息
from django.contrib import messages
# 瀏覽訂位資訊
# 當使用者未登入，而存取首頁的網址時，將使用者導向到登入畫面。
@login_required(login_url="/cms/rest_system/")
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
        'dateTimeNow': datetime.now(),  # 比較用
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
            # 存入指定pk資料
            form.reserve_name_confirm = form_name
            form.reserve_email_confirm = form_email
            form.reserve_datetime_confirm = form_datetime
            form.save()
            print("form update!")
    return redirect('/cms/reserve_detail/')


def home(request):
    return render(request, "cms/home.html")


def test(request):
    return render(request, "test.html")


def login(request):
    if request.method == "POST":
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return HttpResponseRedirect('/cms/reserve_detail/')
        else:
            messages.info(request, '登入有誤,請重新登入或連繫系統管理員!')
            return render(request, "cms/home.html")
    else:
        return render(request, "cms/home.html")


def logout(request):
    django_logout(request)
    return redirect('/cms/rest_system/')  # 重新導向到登入畫面
