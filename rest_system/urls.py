"""rest_system URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from line import views
from django.conf.urls.static import static
from django.conf import settings
from django.conf.urls import url, include

urlpatterns = [
    path('admin/', admin.site.urls), #django後臺用
    path('callback', views.callback),#Line bot用
    path('reserve/<str:id>',views.reserve_web_show), #訂位連結用
    path('cms/', include('cms.urls')),#CMS系統用
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
