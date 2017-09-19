from django.conf.urls import include, url
from .views import SendPay2Go,ReturnPay2Go

urlpatterns = [
                  #url(r'^8a043645b608c37ec5577af7d6bbdf94dc5bdc70e12f6c88f3/?$', fbbotView.as_view())
                  url(r'^SendPay2Go/?$', SendPay2Go),
                  url(r'^ReturnPay2Go/?$', ReturnPay2Go),
                  
               ]