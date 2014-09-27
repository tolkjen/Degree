from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^medapp/', include('med.urls', namespace="med")),
)
