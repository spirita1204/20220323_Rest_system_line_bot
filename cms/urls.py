from django.conf.urls import url

from . import views
from django.urls import path

urlpatterns = [
    path('reserve_detail/', views.reserve_detail),
    path('delete/<int:pk>/',views.delete,name="delete"),#刪除用
    path('update/<int:pk>/',views.update,name="update"),#修改用
]
