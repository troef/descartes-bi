from __future__ import absolute_import

from django.conf.urls import patterns, url

from .views import display

urlpatterns = patterns('',
    url(r'^dash_list/(?P<dash_id>\d+)/$', display),
)
