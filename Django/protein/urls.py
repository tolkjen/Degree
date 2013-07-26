from django.conf.urls import patterns, url

from protein import views

urlpatterns = patterns('',
	# ex: /protein/
	url(r'^$', views.index, name='index'),
	# ex: /protein/upload/
	url(r'^upload/$', views.upload, name='upload'),
)
