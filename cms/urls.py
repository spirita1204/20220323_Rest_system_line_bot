from django.conf.urls import url

from . import views
from django.urls import path

urlpatterns = [
    path('reserve_detail/', views.reserve_detail),      #後台用
    path('delete/<int:pk>/',views.delete,name="delete"),#刪除用
    path('update/<int:pk>/',views.update,name="update"),#修改用
    path('create/',views.create,name="create"),         #新增用

    path('rest_system/',views.home),                    #主頁用
    path('test/',views.test),                           #測試用

    path('login/',views.login,name="login"),            #登入用
    path('logout/', views.logout, name='logout'),       #登出用
]
