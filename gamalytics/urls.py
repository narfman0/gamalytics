from django.conf.urls import patterns, url

from gamalytics import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<gamename>\w+)/$', views.detail, name='detail'),
)

