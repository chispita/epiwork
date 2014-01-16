# -*- coding: utf-8 -*-
from datetime import datetime

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
logger = logging.getLogger(__name__)


survey_form_helper = None
profile_form_helper = None

def get_active_survey_user(request):
    # Obtain the survey user by the gid argument!
    function = 'def get_active_survey_user'
    logger.info('%s' % function)
    gid = request.GET.get('gid', None)

    logger.info('%s - Gid: %s' % (function, gid))
    if gid is None:
        logger.info('%s - Gid is None' % function)
        return None
    else:
        try:
            logger.info('%s - user: % s' % (function, request.user))
            return models.SurveyUser.objects.get(global_id=gid,
                                                 user=request.user)
        except models.SurveyUser.DoesNotExist:
            raise ValueError()

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

    logger.info('_get_person_health_status')

    # habria que revisar request.user.id
    data = survey.get_last_participation_data(request.user.id, global_id)
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

    logger.info('_get_person_is_female')

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
def survey_data(request, survey_shortname, id=0):

    function = 'survey_data'
    logger.info('%s' % function)
    logger.info('%s - survey_name:%s' % (function, survey_shortname))
    logger.info('%s - id:%s' % (function, id))


    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()

    if survey_user is None:
        logger.info('%s - survey_user is None' % function)
        return HttpResponseRedirect(reverse(group_management))
    
    return pollster_views.survey_results_intake(request, survey_shortname, id)

@login_required
def survey_management(request):
    function = 'survey_management'
    logger.info('%s' % function)
    
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()

    if survey_user is None:
        logger.info('%s - survey_user is None' % function)
        return HttpResponseRedirect(reverse(group_management))

    # Get Survey Data
    intake = pollster.models.Survey.get_by_shortname('intake')
    monthly =  pollster.models.Survey.get_by_shortname('monthly')

    # Get last survey date
    survey = monthly if monthly else intake
    last_survey= survey.get_last_participation_data(request.user.id, survey_user.global_id)

    # Query to obtain survey data
    survey_intake = pollster.models.ResultsIntake.objects.all().filter(user=request.user)
    survey_monthly = pollster.models.ResultsMonthly.objects.all().filter(user=request.user)

    template = 'survey/survey_management.html'
    return render_to_response( template, {
            'person': survey_user,
            'last_survey' : last_survey,
            'intake' : survey_intake,
            'monthly' : survey_monthly
            }, context_instance=RequestContext(request))

@login_required
def group_management(request):
    logger.info('group_management')

    try:
        survey = pollster.models.Survey.get_by_shortname('weekly')
    except:
        raise Exception("The survey application requires a published survey with the shortname 'weekly'")
    Weekly = survey.as_model()
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        pass

    if request.method == "POST":
        global_ids = request.POST.getlist('global_ids')

        for survey_user in request.user.surveyuser_set.filter(global_id__in=global_ids):
            if request.POST.get('action') == 'healthy':
                Weekly.objects.create(
                    user=request.user.id,
                    global_id=survey_user.global_id,
                    Q1_0=True, # Q1_0 => "No symptoms. The other fields are assumed to have the correct default information in them.
                    timestamp=datetime.now(),
                )
            elif request.POST.get('action') == 'delete':
                survey_user.deleted = True
                survey_user.save()

    #
    #history = list(_get_health_history(request, survey))
    persons = models.SurveyUser.objects.filter(user=request.user, deleted=False)
    #persons_dict = dict([(p.global_id, p) for p in persons])
    #for item in history:
    #    item['person'] = persons_dict.get(item['global_id'])
    #for person in persons:
    #    person.health_status, person.diag = _get_person_health_status(request, survey, person.global_id)
    #    person.health_history = [i for i in history if i['global_id'] == person.global_id][-10:]
    #    person.is_female = _get_person_is_female(person.global_id)

    template = 'survey/group_management.html'
    return render_to_response( template, {
            'person': survey_user,
            'persons' : persons
            }, context_instance=RequestContext(request))

@login_required
def thanks_profile(request):
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        pass
    return render_to_response('survey/thanks_profile.html', {'person': survey_user},
        context_instance=RequestContext(request))

@login_required
def select_user(request, template='survey/select_user.html'):
    # select_user is still used in some cases: notably when there are unqualified calls to
    # 'profile_index'. So we've not yet removed this template & view.
    # Obviously it's a good candidate for refactoring.

    function= 'def select_user'
    logger.info(function)

    next = request.GET.get('next', None)
    if next is None:
        next = reverse(index)

    users = models.SurveyUser.objects.filter(user=request.user, deleted=False)
    total = len(users)
    if total == 0:
        logger.info('%s - Create SurveyUser: %s %s' % (function, request.user, request.user.username))
        survey_user = models.SurveyUser.objects.create(
            user=request.user,
            name=request.user.username,
        )
        url = '%s?gid=%s' % (next, survey_user.global_id)
        return HttpResponseRedirect(url)
        
    elif total == 1:
        logger.info('%s - Ya existie SurveyUser: %s %s' % (function, request.user, request.user.username))
        survey_user = users[0]
        url = '%s?gid=%s' % (next, survey_user.global_id)
        return HttpResponseRedirect(url)

    return render_to_response(template, {
        'users': users,
        'next': next,
    }, context_instance=RequestContext(request))


@login_required
def survey_intake(request, next=next):
    function = 'def survey_intake'
    logger.info('%s' % function)
    logger.info('%s: user.id:%s user.username:%s' % (function, request.user.id, request.user.username))

    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()

    if survey_user is None:
        url = '%s?next=%s' % (reverse(select_user), reverse(profile_index))
        return HttpResponseRedirect(url)

    logger.info('%s: survey_user' % survey_user)
    return pollster_views.survey_run(request, 'intake' , next=next)

@login_required
def index(request):
    # this is the index for a actual survey-taking
    # it falls back to 'group management' if no 'gid' is provided.
    # i.e. it expects gid to be part of the request!
    function = 'def index:'
    logger.info('%s' % function)

    next = request.GET.get('next', None)
    if next is None:
        next = reverse(index)

    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()

    # No me gusta mucho esta parte
    if survey_user is None:
        url = '%s?next=%s' % (reverse(select_user), reverse(profile_index))
        logger.info('%s - url: %s' % (function, url))
        return HttpResponseRedirect(url)

    # Check if the user has filled user profile
    logger.info('%s- Check Profile' % function)
    profile = pollster_utils.get_user_profile(request.user.id, survey_user.global_id)

    if profile is None:
        logger.info('%s- Check Profile is None' % function)
        # If the user does not complete the Intake form this is the moment
        messages.add_message(request, messages.INFO, 
            _(u'Before we take you to the electric questionnaire, please complete the short background questionnaire below. You will only have to complete this once.'))

        # Redireccion al intake
        url = reverse('apps.survey.views.survey_intake')
        #  check if we need back to views.index
        url_next = reverse('apps.survey.views.survey_management')
        url = '%s?gid=%s&next=%s' % (url, survey_user.global_id, url_next)
        return HttpResponseRedirect(url)
        # check if we need back to views.index)

    try:
        # Busqueda para saber si ha rellenado el formulario inicial

        survey = pollster.models.Survey.get_by_shortname('monthly')

        #daiys = 0
        #logger.info('%s - user: %s, global_id: %s' % (function, request.user.id, survey_user.global_id))
        #last = survey.get_last_participation_data(request.user.id, survey_user.global_id)
        #if last:
        #    dt = datetime.now() - last['timestamp']
        #    logger.info('%s - timestamp: %s days:%s' % (function, last['timestamp'], dt.days))
    
    except Exception as e:
        logger.info('%s - except: %s (%s)' % (function, e.message, type(e)))
        raise Exception("The survey application requires a published survey with the shortname %s" % survey_name)

    next = None
    if 'next' not in request.GET:
        next = reverse(group_management) # is this necessary? Or would it be the default?

    return pollster_views.survey_run(request, survey.shortname, next=next)

    # If there are more than 30 days let complet another survey
    #if dt.days > 29:
    #    logger.info('%s - shortname: %s' % (function, survey.shortname))
    #    return pollster_views.survey_run(request, survey.shortname, next=next)
    #else:        
    #    return thanks_profile(request)

    #    template = 'survey/completed.html'
    #    return render_to_response(template, {
    #            'person': survey_user
    #            }, context_instance=RequestContext(request))

def query_to_dicts(query_string, *query_args):
    """Run a simple query and produce a generator
    that returns the results as a bunch of dictionaries
    with keys for the column values selected.
    """

    logger.info('query_to_dicts')

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
    logger.info(function)

    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()

    if survey_user is None:
        url = '%s?next=%s' % (reverse(select_user), reverse(profile_index))
        return HttpResponseRedirect(url)

    # Query to obtain survey headers
    survey = pollster.models.Survey.get_by_shortname('intake')
    logger.info('Survey: %s' % survey)

    # Query to obtain survey data
    data = pollster.models.ResultsIntake.get_by_user(request.user.id)
      
    # survery_data 
    logger.info('Data: %s' % data)
    return render_to_response('survey/profile_electric.html', {
            "user": survey_user,
            "survey": survey,
            "data": data,
        },context_instance=RequestContext(request))

@login_required
def profile_index(request):
    # this appears to be ready-for-cleanup; but at this moment I (KvS) cannot be absolutely
    # sure and don't have the time to check, so I'll leave it.

    # what does this do? if no "gid" parameter is presented in the GET, 'select_user' is
    # called to select the user.
    # if one is present, 
    function = 'def profile_index'
    logger.info(function)

    try:
        logger.info('%s - Search survey_user' % function)
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()

    if survey_user is None:
        logger.info('%s - survey_user is None' % function)
        url = '%s?next=%s' % (reverse(select_user), reverse(profile_index))
        logger.info('%s - url: %s' % (function, url))
        return HttpResponseRedirect(url)

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

    return pollster_views.survey_run(request, survey.shortname, next=next)


def main_index(request):
    # the generalness of the name of this method reflects the mess that the various
    # indexes have become. 

    # this is the one that does the required redirection for the button 'my account'
    # i.e. to group if there is a group, to the main index otherwise


    if models.SurveyUser.objects.filter(user=request.user, deleted=False).count() != 1:
        return HttpResponseRedirect(reverse(profile_index))

    gid = models.SurveyUser.objects.get(user=request.user, deleted=False).global_id
    return HttpResponseRedirect(reverse(index) + '?gid=' + gid)


    function = 'def Main Index'
    logger.info(function)

    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        # Si no existe llamara a profile_index que crea el survey_user
        logger.error('%s - Main_Index: Vaue Error' % function)
        return HttpResponseRedirect(reverse(profile_index))

    logger.info('%s - SurveyUser: %s' % (function, survey_user))

    try:
        gid = models.SurveyUser.objects.get(user=request.user, deleted=False).global_id
    except models.SurveyUser.DoesNotExist:
        gid = None

    logger.info('%s - Gid: %s' % (function,gid))
    if gid:
        return HttpResponseRedirect(reverse(index) + '?gid=' + gid)
    else:
        return HttpResponseRedirect(reverse(profile_index))


@login_required
def people_edit(request):

    logger.info('people_edit')

    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()

    if survey_user is None:
        url = '%s?next=%s' % (reverse(select_user), reverse(people_edit))
        return HttpResponseRedirect(url)
    elif survey_user.deleted == True:
        raise Http404()

    if request.method == 'POST':
        form = forms.AddPeople(request.POST)
        if form.is_valid():
            survey_user.name = form.cleaned_data['name']
            survey_user.save()

            return HttpResponseRedirect(reverse(group_management))

    else:
        form = forms.AddPeople(initial={'name': survey_user.name})

    return render_to_response('survey/people_edit.html', {'form': form},
                              context_instance=RequestContext(request))

@login_required
def people_remove(request):

    logger.info('people_remove')
    try:
        survey_user = get_active_survey_user(request)
    except ValueError:
        raise Http404()

    if survey_user is None:
        url = reverse(group_management)
        return HttpResponseRedirect(url)
    elif survey_user.deleted == True:
        raise Http404()

    confirmed = request.POST.get('confirmed', None)

    if confirmed == 'Y':
        survey_user.deleted = True
        survey_user.save()
   
        url = reverse(group_management)
        return HttpResponseRedirect(url)

    elif confirmed == 'N':
        url = reverse(group_management)
        return HttpResponseRedirect(url)

    else:
        return render_to_response('survey/people_remove.html', {'person': survey_user},
                              context_instance=RequestContext(request))

@login_required
def people_add(request):

    logger.info('people_add')
    if request.method == 'POST':
        form = forms.AddPeople(request.POST)
        if form.is_valid():
            survey_user = models.SurveyUser()
            survey_user.user = request.user
            survey_user.name = form.cleaned_data['name']
            survey_user.save()

            messages.add_message(request, messages.INFO, 
                _('A new person has been added.'))

            next = request.GET.get('next', None)
            if next is None:
                url = reverse(group_management)
            else:
                url = '%s?gid=%s' % (next, survey_user.global_id)
            return HttpResponseRedirect(url)

    else:
        form = forms.AddPeople()

    return render_to_response('survey/people_add.html', {'form': form},
                              context_instance=RequestContext(request))


