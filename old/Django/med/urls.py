from django.conf.urls import patterns, url

from med import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),

	url(r'^new/$', views.classification_new, name='classification_new'),
	url(r'^create/$', views.classification_create, name='classification_create'),
	url(r'^list/orderby/(?P<sortby>.+)$', views.classification_list, name='classification_list'),
	url(r'^delete/(?P<id>\d+)/(?P<sortby>.+)$', views.classification_delete, name='classification_delete'),
	url(r'^details/(?P<id>\d+)/(?P<sortby>.+)$', views.classification_details, name='classification_details'),
)
