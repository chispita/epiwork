from django.conf.urls.defaults import *

from . import views

urlpatterns = patterns('',
    url(r'^profile/$', views.profile_index, name='survey_profile'),
    url(r'^profile/electric/$', views.profile_electric, name='survey_profile_electric'),
    url(r'^profile/intake/$', views.survey_intake, name='survey_profile_intake'),
    url(r'^profile/surveys/$', views.survey_management, name='survey_management'),
    url(r'^main/$', views.main_index),
    url(r'^group_management/$', views.group_management, name='group_management'),
    #url(r'^survey_management/$', views.survey_management, name='survey_management'),
    url(r'^survey_data/(?P<survey_shortname>.+)/(?P<id>\d+)/$', views.survey_data, name='survey_data'),
    #url(r'^survey_data/(?P<survey_shortname>.+)/$', views.survey_data, name='survey_data'),
    #url(r'intake/$', views.survey_intake, name='survey_intake'),
    url(r'^thanks_profile/$', views.thanks_profile, name='profile_thanks'),
    url(r'^select/$', views.select_user, name='survey_select_user'),
    url(r'^$', views.index, name='survey_index'),
)
