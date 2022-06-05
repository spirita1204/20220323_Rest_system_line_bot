from django.shortcuts import render
from .ecpay import main
from django.http import HttpResponseRedirect,HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
# Create your views here.

def success_pay(request):
    return render(request, 'payment/success.html')

def fail_pay(request):
    return render(request, 'payment/fail.html')

@csrf_exempt
def end_page(request):
    print("to user server")
    if request.method == 'GET':
        return HttpResponseRedirect(reverse('payment:fail'))

    if request.method == 'POST':
        result = request.POST.get('RtnMsg')
        print(result)
        if result == 'Succeeded':
            print("#######")
            print(request.POST.get('TradeNo') )
            print(request.POST.get('TradeAmt'))
            print(request.POST.get('TradeDate'))
            check = request.POST.get('CheckMacValue')
            print(check)
            print("#######")
            
            return HttpResponseRedirect(reverse('payment:success'))
        # 判斷失敗
        else:
            return HttpResponseRedirect(reverse('payment:fail'))

def end_return(request):
    if request.method == 'POST':
        return '1|OK'