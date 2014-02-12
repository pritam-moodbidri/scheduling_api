from django.conf.urls import patterns, include, url


urlpatterns = patterns('',
    url(r'^scheduler/', include('Scheduler.urls')),
)
