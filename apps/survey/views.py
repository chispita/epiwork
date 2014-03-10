# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil import relativedelta

from django import forms
from django.template import Context, loader, RequestContext
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.db import connection, transaction, DatabaseError
from django.core.urlresolvers import reverse
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.db import connection

from apps.survey import utils, models, forms
from apps.pollster import views as pollster_views
from apps.pollster import utils as pollster_utils
from .survey import ( Specification,
                      FormBuilder,
                      JavascriptBuilder,
                      get_survey_context, )


import apps.pollster as pollster
import pickle
import logging
logger = logging.getLogger('logview.userlogins')  #

survey_form_helper = None
profile_form_helper = None

def X_decode_person_health_status(status):
    d = {
        "NO-SYMPTOMS":                                  _('No symptoms'),
        "ILI":                                          _('Flu symptoms'),
        "COMMON-COLD":                                  _('Common cold'),
        "GASTROINTESTINAL":                             _('Gastrointestinal symptoms'),
        "ALLERGY-or-HAY-FEVER-and-GASTROINTESTINAL":    _('Allergy / hay fever and gastrointestinal symptoms'),
        "ALLERGY-or-HAY-FEVER":                         _('Allergy / hay fever'),
        "COMMON-COLD-and-GASTROINTESTINAL":             _('Common cold and gastrointestinal symptoms'),
        "NON-SPECIFIC-SYMPTOMS":                        _('Other non-influenza symptons'),
    }
    if status in d:
        return d[status]

    return _('Unknown')

def X_get_person_health_status(request, survey, global_id):

    logger.debug('_get_person_health_status')

    # habria que revisar request.user.id
    data = survey.get_last_participation_data(request.user.id)
    status = None
    if data:
        cursor = connection.cursor()
        params = { 'weekly_id': data["id"] }
        queries = {
            'sqlite':"""
            SELECT S.status
              FROM pollster_health_status S
             WHERE S.pollster_results_weekly_id = :weekly_id""",
            'mysql':"""
            SELECT S.status
              FROM pollster_health_status S
             WHERE S.pollster_results_weekly_id = :weekly_id""",
            'postgresql':"""
            SELECT S.status
              FROM pollster_health_status S
             WHERE S.pollster_results_weekly_id = %(weekly_id)s"""
        }
        cursor.execute(queries[utils.get_db_type(connection)], params)
        status = cursor.fetchone()[0]
    return (status, _decode_person_health_status(status))

def X_get_person_is_female(global_id):

    logger.debug('_get_person_is_female')

    try:
        cursor = connection.cursor()
        queries = {
            'sqlite':"""SELECT Q1 FROM pollster_results_intake WHERE global_id = %s""",
            'mysql':"""SELECT `Q1` FROM pollster_results_intake WHERE `global_id` = %s""",
            'postgresql':"""SELECT "Q1" FROM pollster_results_intake WHERE "global_id" = %s""",
        }
        cursor.execute(queries[utils.get_db_type(connection)], [global_id,])
        return cursor.fetchone()[0] == 1 # 0 for male, 1 for female
    except:
        return None

def X_get_health_history(request, survey):
    results = []
    cursor = connection.cursor()
    params = { 'user_id': request.user.id }
    queries = {
        'sqlite':"""
            SELECT W.timestamp, W.global_id, S.status
              FROM pollster_health_status S, pollster_results_weekly W
             WHERE S.pollster_results_weekly_id = W.id
               AND W.user = :user_id
             ORDER BY W.timestamp""",
        'mysql':"""
            SELECT W.timestamp, W.global_id, S.status
              FROM pollster_health_status S, pollster_results_weekly W
             WHERE S.pollster_results_weekly_id = W.id
               AND W.user = :user_id
             ORDER BY W.timestamp""",
        'postgresql':"""
            SELECT W.timestamp, W.global_id, S.status
              FROM pollster_health_status S, pollster_results_weekly W
             WHERE S.pollster_results_weekly_id = W.id
               AND W.user = %(user_id)s
             ORDER BY W.timestamp""",
    }
    cursor.execute(queries[utils.get_db_type(connection)], params)
    results = cursor.fetchall()
    for ret in results:
        timestamp, global_id, status = ret
        survey_user = models.SurveyUser.objects.get(global_id=global_id)
        yield {'global_id': global_id, 'timestamp': timestamp, 'status': status, 'diag':_decode_person_health_status(status), 'survey_user': survey_user}

@login_required
def survey_data(request, survey_shortname="intake", id=0):
    function = 'def survey_data'
    logger.debug('%s' % function)
    logger.debug('%s - survey_name:%s' % (function, survey_shortname))
    logger.debug('%s - id:%s' % (function, id))

    logger.debug('%s - pollster(1)' % function)
    return pollster_views.pollster_data(request, survey_shortname, id)

@login_required
def survey_data_monthly(request, id):
    function = 'def survey_data_monthly'
    logger.debug('%s' % function)

    return survey_data(request,"monthly", id)

@login_required
def survey_update(request, survey_shortname="intake", id=0):
    function = 'def survey_update'
    logger.debug('%s' % function)
    logger.debug('%s - survey_name:%s' % (function, survey_shortname))
    logger.debug('%s - id:%s' % (function, id))

    logger.debug('%s - pollster(1)' % function)
    return pollster_views.pollster_update(request, survey_shortname, id)

@login_required
def survey_update_monthly(request, id):
    function = 'def survey_update_monthly'
    logger.debug('%s' % function)

    return survey_update(request,"monthly", id)

@login_required
def survey_management(request):
    function = 'survey_management'
    logger.debug('%s' % function)

    # Get Survey Data
    intake = pollster.models.Survey.get_by_shortname('intake')
    monthly =  pollster.models.Survey.get_by_shortname('monthly')

    # Get last survey date
    survey = monthly if monthly else intake
    last_survey= survey.get_last_participation_data(request.user.id)

    # Query to obtain survey data
    survey_intake = pollster.models.ResultsIntake.objects.all().filter(user=request.user)
    survey_monthly = pollster.models.ResultsMonthly.objects.all().filter(user=request.user)

    template = 'survey/survey_management.html'
    return render_to_response( template, {
            #'person': survey_user,
            'last_survey' : last_survey,
            'intake' : survey_intake,
            'monthly' : survey_monthly
            }, context_instance=RequestContext(request))

@login_required
def survey_general_data_update(request):
    # Update data of survey intake
    function = 'def survey_update'
    logger.debug('%s' % function)

    survey_shortname="intake"
    id=0
    # Get Survey Data
#    intake = pollster.models.Survey.get_by_shortname('intake')

    # Query to obtain survey data
#Missing to filter by tag
#    survey_intake = pollster.models.ResultsIntake.objects.all().filter(user=request.user)

    logger.debug('%s - survey_name:%s' % (function, survey_shortname))
    logger.debug('%s - id:%s' % (function, id))
    return pollster_views.pollster_update(request, survey_shortname, id)

@login_required
def thanks_profile(request):
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        pass
    return render_to_response('survey/thanks_profile.html', {'person': survey_user},
        context_instance=RequestContext(request))

@login_required
def show_message(request):
    ''' Show completed template '''
    function='def show_message'
    logger.debug(function)

    return render_to_response(
            'survey/completed.html',
            context_instance=RequestContext(request))

@login_required
def survey_intake_view(request, survey_shortname="intake", id=0):
    # Get data of Survey Intake
    function = 'def survey_data'
    logger.debug('%s' % function)
    logger.debug('%s - survey_name:%s' % (function, survey_shortname))
    logger.debug('%s - id:%s' % (function, id))
    return pollster_views.pollster_data(request, survey_shortname, id)


@login_required
def survey_intake_update(request, category=""):
    # Update data of survey intake
    function = 'def survey_update'

    id=0
    shortname = 'intake'

    logger.debug('%s' % function)
    #logger.debug('%s - survey_name:%s' % (function, survey_shortname))
    logger.debug('%s - id:%s' % (function, id))
    logger.debug('%s - category:%s' % (function, category))

    return pollster_views.pollster_update(request, shortname, category, id)

@login_required
def survey_intake(request, next=next):
    function = 'def survey_intake'
    logger.debug('%s' % function)
    logger.debug('%s: user.id:%s user.username:%s' % (function, request.user.id, request.user.username))

    # Check user has not filled in the intake survey, in such a case do not display the message
    survey = pollster.models.Survey.get_by_shortname('intake')
    last = survey.get_last_participation_data(request.user.id)
    if last:
	pass
    else:
	messages.info(request, _("You need to complete the initial survey, please."))

    logger.debug('%s: survey_user(1)' % function)
    return pollster_views.pollster_run(request, 'intake' , next=next)

@login_required
def profile_index(request):
    # this appears to be ready-for-cleanup; but at this moment I (KvS) cannot be absolutely
    # sure and don't have the time to check, so I'll leave it.

    # what does this do? if no "gid" parameter is presented in the GET, 'select_user' is
    # called to select the user.
    # if one is present,
    function = 'def profile_index'
    logger.debug(function)

    try:
        '''
        DIC/22/13 CVG
        Faltaria comprobar si ha rellenado el intake
        para que complete el monthly
        '''
        survey = pollster.models.Survey.get_by_shortname('intake')
    except:
        raise Exception("The survey application requires a published survey with the shortname 'intake'")

    next = None
    if 'next' not in request.GET:
        next = reverse(thanks_profile)

    return pollster_views.pollster_run(request, survey.shortname, next=next)

@login_required
def index(request):
    # this is the index for a actual survey-taking
    # it falls back to 'group management' if no 'gid' is provided.
    # i.e. it expects gid to be part of the request!
    function = 'def index:'
    logger.debug('%s' % function)
    logger.debug('%s User:%s' % (function, request.user.id))

    dt = 0
    survey_name = 'monthly'
    next = request.GET.get('next', None)
    if next is None:
        next = reverse(index)


    # Check if the user has filled user profile
    logger.debug('%s- Check Profile' % function)
    profile = pollster_utils.get_user_profile(request.user.id)

    if profile is None:
        logger.debug('%s- Check Profile is None' % function)
        next = reverse('apps.survey.views.survey_management')
        return survey_intake(request, next=next)

    try:
        # Busqueda para saber si ha rellenado el formulario monthly
        survey = pollster.models.Survey.get_by_shortname(survey_name)

    except Exception as e:
        logger.debug('%s - except: %s (%s)' % (function, e.message, type(e)))
        raise Exception("The survey application requires a published survey with the shortname %s" % survey_name)

    next = None
    if 'next' not in request.GET:
        next = reverse(survey_management) # is this necessary? Or would it be the default?

    logger.debug('%s - user: %s' % (function, request.user.id))
    last = survey.get_last_participation_data(request.user.id)
    if last:
        datenow = datetime.now()

        #datenow = datetime.strptime(str('2014-06-15'), '%Y-%m-%d')

        if datenow.month != last['timestamp'].month:
            logger.debug('%s - shortname: %s' % (function, survey.shortname))
            logger.debug('%s: survey_user(2)' % function)

	    # Since we want to redirect monthly survey queries to intake
            # questionnaire update so data is updated there, we check if
            # the shortname is monthly and in that case redirect to the
            # update of intake questionnaire
#	    if survey.shortname == 'monthly':
#			# Redirection to intake update
#			return pollster_views.pollster_update(request, 'intake', 'records', 0)
#	    else:
#	        	return pollster_views.pollster_run(request, survey.shortname, next=next)
	    logger.debug('Display records')
	    return survey_intake_update(request, "records")
        else:
            messages.info(request, _("You have done the survey in course, please come back in few days and you will complete a new one."))
            return show_message(request)
    else:
        logger.debug('%s - shortname(2): %s' % (function, survey.shortname))

        logger.debug('%s: survey_user(3)' % function)

	# Since we want to redirect monthly survey queries to intake
	# questionnaire update so data is updated there, we check if
	# the shortname is monthly and in that case redirect to the
	# update of intake questionnaire
	if survey.shortname == 'monthly':
		# Redirection to intake update
        	return pollster_views.pollster_update(request, 'intake', 'records', 0)
	else:
              	return pollster_views.pollster_run(request, survey.shortname, next=next)

def query_to_dicts(query_string, *query_args):
    """Run a simple query and produce a generator
    that returns the results as a bunch of dictionaries
    with keys for the column values selected.
    """

    logger.debug('query_to_dicts')

    cursor = connection.cursor()
    cursor.execute(query_string, query_args)
    col_names = [desc[0] for desc in cursor.description]

    while True:
        row = cursor.fetchone()
        if row is None:
            break
        row_dict = dict(izip(col_names, row))
        yield row_dict

    return

@login_required
def profile_electric(request):
    function = ('Profile_Electric')
    logger.debug(function)

    # Query to obtain survey headers
    survey = pollster.models.Survey.get_by_shortname('intake')
    logger.debug('Survey: %s' % survey)

    # Query to obtain survey data
    data = pollster.models.ResultsIntake.get_by_user(request.user.id)

    # survery_data
    logger.debug('Data: %s' % data)
    return render_to_response('survey/profile_electric.html', {
            "user": survey_user,
            "survey": survey,
            "data": data,
        },context_instance=RequestContext(request))

def main_index(request):
    # the generalness of the name of this method reflects the mess that the various
    # indexes have become.

    # this is the one that does the required redirection for the button 'my account'
    # i.e. to group if there is a group, to the main index otherwise
    function = 'def Main Index'
    logger.debug(function)

    return HttpResponseRedirect(reverse(index))
