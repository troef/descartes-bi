from django.conf.urls import patterns, url
from libre_driver import views

urlpatterns = patterns('',
                       # ex: /libre/
                       url(r'^$', views.IndexView, name='index'),
                       )
