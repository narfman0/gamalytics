from django.conf.urls import patterns, url

from gamalytics import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^s/$', views.search),
    url(r'^g/(?P<gamename>\w+)/$', views.detail, name='detail'),
)

