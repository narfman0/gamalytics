from django.conf.urls import patterns, include, url
from django.contrib import admin
from gamalytics import views
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index, name='index'),
    url(r'^s/$', views.search),
    url(r'^update', views.update),
    url(r'^g/(?P<name>[\w|\W]+)/$', views.game),
)

