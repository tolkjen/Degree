from django.conf.urls import patterns, url

from med import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),

	url(r'^validate/new/$', views.validate_new, name='validate_new'),
	url(r'^validate/post/$', views.validate_post, name='validate_post'),
	url(r'^validate/list/$', views.validate_list, name='validate_list'),
	url(r'^validate/delete/(?P<id>\d+)$', views.validate_delete, name='validate_delete'),
)
