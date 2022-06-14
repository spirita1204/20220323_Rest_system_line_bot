from django.shortcuts import render,redirect
from .forms import CheckoutModelForm
from payment.ecpay import main
from django.http import HttpResponseRedirect,HttpResponse
# Create your views here.

def itemList(request):
    print("itemList!")
    # 導向買單頁面checkout
    if request.method == 'POST':
        # https://ithelp.ithome.com.tw/articles/10236351
        # redirect進行跳轉,render只進行渲染
        return redirect("/shop/checkout/")
    # 重新導回itemList
    else:
        return render(request, "product/itemList.html")

def checkout(request):
    print("checkout!")
    CheckoutForm = CheckoutModelForm()

    if request.method == "POST":
        #存訂單成立資料
        form = CheckoutModelForm(request.POST)
        if form.is_valid():
            form_order_name = form["order_name"].value()
            form_order_email = form["order_email"].value()
            form_order_address = form["order_address"].value()
            form_order_item = form["order_item"].value()
            form_order_price = form["order_price"].value()

            form.order_name = form_order_name
            form.order_email = form_order_email
            form.order_address = form_order_address
            form.order_item = form_order_item
            form.order_price = form_order_price
            order = form.save()
            #order id存哪筆訂單資料
        print("ECPay")
        #導向ECPay金流頁面
        return HttpResponse(main(order.id,form_order_item))
    context = {
        'checkoutForm' : CheckoutForm
    }
    return render(request, "product/checkout.html", context)