from django.conf.urls import patterns, include
from django.contrib import admin
from gamalytics import views
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^$', views.index),
    (r'^s/$', views.search),
    (r'^update', views.update),
    (r'^g/(?P<name>[\w|\W]+)/$', views.game),
    (r'^login/$', 'django.contrib.auth.views.login'),
    (r'^logout/$', views.logout),
    (r'^register/$', views.register),
    (r'^registerrequest/$', views.registerrequest),
)