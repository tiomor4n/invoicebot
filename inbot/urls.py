from django.conf.urls import include, url
from .views import callback,checklog,refreshlog

urlpatterns = [
                  #url(r'^8a043645b608c37ec5577af7d6bbdf94dc5bdc70e12f6c88f3/?$', fbbotView.as_view())
                  url(r'^linebot/?$', callback),
                  url(r'^checklog/?$', checklog),
                  url(r'^refreshlog/?$', refreshlog),
               ]