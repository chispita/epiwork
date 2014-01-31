from django.conf.urls.defaults import *

from . import views

urlpatterns = patterns('',
    url(r'^profile/$', views.profile_index, name='survey_profile'),
    url(r'^profile/electric/$', views.profile_electric, name='survey_profile_electric'),
    url(r'^profile/surveys/$', views.survey_management, name='survey_management'),
    url(r'^main/$', views.main_index),
    url(r'^survey_management/$', views.survey_management, name='survey_management'),

    url(r'^intake/view/$', views.survey_intake_view, name='survey_intake_view'),
    url(r'^intake/update/$', views.survey_intake_update, name='survey_intake_update'),

    url(r'^monthly/(?P<id>\d+)/$', views.survey_monthly ,name='survey_monthly'),
    url(r'^monthly/(?P<id>\d+)/update/$', views.survey_monthly_update ,name='survey_monthly_update'),

    url(r'^thanks_profile/$', views.thanks_profile, name='profile_thanks'),
    #url(r'^select/$', views.select_user, name='survey_select_user'),
    url(r'^$', views.index, name='survey_index'),
)
