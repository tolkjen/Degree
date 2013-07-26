from django.conf.urls import patterns, url

from med import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),

	url(r'^trained/$', views.trained_list, name='trained_list'),
	url(r'^trained/new/$', views.trained_list_new, name='trained_list_new'),
	url(r'^trained/delete/(?P<id>\d+)$', views.trained_list_delete, name='trained_list_delete'),

	url(r'^results/$', views.cls_list, name='cls_list'),
	url(r'^results/datalist/$', views.cls_list_new, name='cls_list_new'),
	url(r'^results/new/(?P<id>\d+)$', views.cls_list_new_form, name='cls_list_new_form'),
	url(r'^results/delete/(?P<id>\d+)$', views.cls_list_delete, name='cls_list_delete'),
	url(r'^results/preview/(?P<id>\d+)$', views.cls_list_preview, name='cls_list_preview'),
)
