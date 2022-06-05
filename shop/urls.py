from django.conf.urls import url

from . import views
from django.urls import path

urlpatterns = [
    path('itemList/', views.itemList),      #商品欄用
    path('checkout/', views.checkout),      #結帳用
]
