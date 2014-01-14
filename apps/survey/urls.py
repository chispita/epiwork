from django.conf.urls.defaults import *

from . import views

urlpatterns = patterns('',
    url(r'^profile/$', views.profile_index, name='survey_profile'),
    url(r'^profile/electric/$', views.profile_electric, name='survey_profile_electric'),
    url(r'^main/$', views.main_index),
    url(r'^group_management/$', views.group_management, name='group_management'),
    url(r'^survey_management/$', views.survey_management, name='survey_management'),
    url(r'^survey_data/$', views.survey_data, name='survey_management'),
    url(r'^thanks_profile/$', views.thanks_profile, name='profile_thanks'),
    url(r'^$', views.index, name='survey_index'),
)
