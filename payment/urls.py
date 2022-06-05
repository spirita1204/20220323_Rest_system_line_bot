from django.conf.urls import url
from . import views
urlpatterns = [
    #ECPay
    url(r'^success/$', views.success_pay
        , name='success'),
    url(r'^fail/$', views.fail_pay
        , name='fail'),
    url(r'^end_page/$', views.end_page
        , name='end_page'),
]
