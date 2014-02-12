from django.conf.urls import patterns, url
from Scheduler.views import ActivityInstanceView


urlpatterns = patterns('',
    url(r'activityinstances/(?P<activity_instance_id>.*)/', ActivityInstanceView.as_view(),
        name='activity_instance_view')
)