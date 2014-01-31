# -*- coding: utf-8 -*-
from django.utils import simplejson
from django.core.urlresolvers import get_resolver, reverse
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, render_to_response, redirect, get_object_or_404
from django.utils.safestring import mark_safe
from django.utils.translation import to_locale, get_language, ugettext as _
from django.template import RequestContext
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import authenticate, login
from django.conf import settings

from cms import settings as cms_settings
from apps.survey.models import SurveyUser
from .utils import get_user_profile
from . import models, forms, fields, parser, json
import re, datetime, locale, csv, urlparse, urllib

import logging
logger = logging.getLogger('logview.userlogins')

def request_render_to_response(req, *args, **kwargs):
    kwargs['context_instance'] = RequestContext(req)
    return render_to_response(*args, **kwargs)

def get_object_or_none(model, **kwargs):
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def retry(f, *args, **kwargs):
    tries = 2
    while tries:
        try:
            return f(*args, **kwargs)
        except:
            tries -= 1
            if tries == 0:
                raise

#@staff_member_required
def survey_list(request):
    function = 'def Survey list'
    logger.info('%s' % function)
    surveys = models.Survey.objects.all()
    form_import = forms.SurveyImportForm()
    return request_render_to_response(request, 'pollster/survey_list.html', {
        "surveys": surveys,
        "form_import": form_import
    })

@staff_member_required
def survey_add(request):
    function = 'def Survey add'
    logger.info('%s' % function)
    survey = models.Survey()
    if (request.method == 'POST'):
        form = forms.SurveyXmlForm(request.POST)
        if form.is_valid():
            # create and redirect
            parser.survey_update_from_xhtml(survey, form.cleaned_data['surveyxml'])
            return redirect(survey)
    # return an empty survey structure
    virtual_option_types = models.VirtualOptionType.objects.all()
    question_data_types = models.QuestionDataType.objects.all()
    rule_types = models.RuleType.objects.all()
    return request_render_to_response(request, 'pollster/survey_edit.html', {
        "survey": survey,
        "virtual_option_types": virtual_option_types,
        "question_data_types": question_data_types,
        "rule_types": rule_types,
        "CMS_MEDIA_URL": cms_settings.CMS_MEDIA_URL,
    })

@staff_member_required
def survey_edit(request, id):
    function = 'def Survey edit'
    logger.info('%s' % function)
    survey = get_object_or_404(models.Survey, pk=id)
    if not survey.is_editable:
        return redirect(survey_test, id=id)
    if request.method == 'POST':
        logger.info('%s- POST' % function)
        form = forms.SurveyXmlForm(request.POST)
        if form.is_valid():
            logger.info('%s- is_valid' % function)
            parser.survey_update_from_xhtml(survey, form.cleaned_data['surveyxml'])
            logger.info('%s- Suvey:%s' % (function, survey))
            return redirect(survey)
    virtual_option_types = models.VirtualOptionType.objects.all()
    question_data_types = models.QuestionDataType.objects.all()
    rule_types = models.RuleType.objects.all()
    return request_render_to_response(request, 'pollster/survey_edit.html', {
        "survey": survey,
        "virtual_option_types": virtual_option_types,
        "question_data_types": question_data_types,
        "rule_types": rule_types,
        "CMS_MEDIA_URL": cms_settings.CMS_MEDIA_URL,
    })

@staff_member_required
def survey_publish(request, id):
    function = 'def Survey publish'
    logger.info('%s' % function)
    survey = get_object_or_404(models.Survey, pk=id)
    if (request.method == 'POST'):
        errors = survey.publish()
        if errors:
            messages.error(request, 'Unable to publish the survey, please check the errors below')
            for error in errors[:5]:
                messages.warning(request, error)
        return redirect(survey)
    return redirect(survey)

@staff_member_required
def survey_unpublish(request, id):
    function = 'def Survey unpublish'
    logger.info('%s' % function)
    survey = get_object_or_404(models.Survey, pk=id)
    if (request.method == 'POST'):
        survey.unpublish()
        return redirect(survey)
    return redirect(survey)

@staff_member_required
def survey_test(request, id, language=None):
    function = 'def Survey test'
    logger.info('%s' % function)
    survey = get_object_or_404(models.Survey, pk=id)
    if language:
        translation = get_object_or_404(models.TranslationSurvey, survey=survey, language=language)
        survey.set_translation_survey(translation)
    if language is None:
        language = get_language()
    locale_code = locale.locale_alias.get(language)
    if locale_code:
        locale_code = locale_code.split('.')[0].replace('_', '-')
        if locale_code == "en-US":
            locale_code = "en-GB"
    survey_user = _get_active_survey_user(request)
    user = _get_active_survey_user(request)
    form = None
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    last_participation_data = None
    if request.method == 'POST':
        data = request.POST.copy()
        data['user'] = user_id
        data['global_id'] = global_id
        data['user_id'] = survey_user.id
        data['timestamp'] = datetime.datetime.now()

        form = survey.as_form()(data)
        if form.is_valid():
            if language:
                next_url = _get_next_url(request, reverse(survey_test, kwargs={'id':id, 'language': language}))
            else:
                next_url = _get_next_url(request, reverse(survey_test, kwargs={'id':id}))
            return HttpResponseRedirect(next_url)
        else:
            survey.set_form(form)
    encoder = json.JSONEncoder(ensure_ascii=False, indent=2)
    last_participation_data_json = encoder.encode(last_participation_data)

    return request_render_to_response(request, 'pollster/survey_test.html', {
        "language": language,
        "locale_code": locale_code,
        "survey": survey,
        "default_postal_code_format": fields.PostalCodeField.get_default_postal_code_format(),
        "last_participation_data_json": last_participation_data_json,
        "language": language,
        "form": form
    })

def survey_intake(request, next=None):
    function = 'def Survey intake'
    logger.info('%s' % function)
    return pollster_run(request, 'intake', next)

@login_required
def pollster_update(request, shortname, id=0):
    function = 'def pollster update'
    logger.info('%s' % function)

    survey = get_object_or_404(models.Survey, shortname=shortname,status='PUBLISHED')
    logger.info('%s survey:%s' % (function, survey))
    language = get_language()
    locale_code = locale.locale_alias.get(language)
    if locale_code:
        locale_code = locale_code.split('.')[0].replace('_', '-')
        if locale_code == "en-US":
            locale_code = "en-GB"

    translation = get_object_or_none(models.TranslationSurvey, survey=survey, language=language, status="PUBLISHED")
    survey.set_translation_survey(translation)

    user_id = request.user.id
    query = pollster_get_data(user_id,shortname, id)

    form = None
    if request.method == 'POST':
        logger.debug('%s POST' % function)
        data = request.POST.copy()
        data['user'] = user_id
        data['timestamp'] = datetime.datetime.now()
        form = survey.as_form()(data)

        if form.is_valid():
            # como no podía actualizar el campo se borra el registro y
            # lo vuelve a crear
            logger.info('%s - Save Delete' % function)
            query.delete()
            logger.info('%s - Save Update' % function)
            form.save()

            messages.info(request, _("Your survey has been updated"))
            return render(request, 'survey/survey_management.html')
        else:
            survey.set_form(form)

    user_id = request.user.id
    logger.info('%s user_id:%s' % (function, user_id))

    if query is None:
        logger.error('%s: No data' % function)
        messages.error(request, 'Unable to find data with this survey.')
        return request_render_to_response(request, 'pollster/messages.html')

    return request_render_to_response(request, 'pollster/pollster_update.html', {
        "language": language,
        "locale_code": locale_code,
        "survey": survey,
        "data":query,
        "default_postal_code_format": fields.PostalCodeField.get_default_postal_code_format(),
        "form": form
    })

def pollster_run(request, shortname, next=None, clean_template=False):
    function = 'def Pollster run'
    logger.info('%s' % function)

    survey = get_object_or_404(models.Survey, shortname=shortname,status='PUBLISHED')
    language = get_language()
    locale_code = locale.locale_alias.get(language)
    if locale_code:
        locale_code = locale_code.split('.')[0].replace('_', '-')
        if locale_code == "en-US":
            locale_code = "en-GB"

    translation = get_object_or_none(models.TranslationSurvey, survey=survey, language=language, status="PUBLISHED")
    survey.set_translation_survey(translation)

    form = None
    user_id = request.user.id
    last_participation_data = survey.get_last_participation_data(user_id)

    if request.method == 'POST':
        data = request.POST.copy()
        data['user'] = user_id
        data['timestamp'] = datetime.datetime.now()
        form = survey.as_form()(data)
        if form.is_valid():
            logger.info('%s - Save' % function)
            form.save()
            next_url = next or _get_next_url(request, reverse("pollster_run", kwargs={'shortname': shortname}))

            next_url_parts = list(urlparse.urlparse(next_url))
            query = dict(urlparse.parse_qsl(next_url_parts[4]))
            next_url_parts[4] = urllib.urlencode(query)
            next_url = urlparse.urlunparse(next_url_parts)

            # Ejectuara algo despues de la grabacion
            if survey.shortname == 'weekly':
                #__, diagnosis = _get_person_health_status(request, survey, global_id)
                messages.info(request, _("Thanks - your survey"))
            else:
                messages.info(request, _("Thanks for taking the time to fill out this survey."))
            return HttpResponseRedirect(next_url)
        else:
            survey.set_form(form)

    encoder = json.JSONEncoder(ensure_ascii=False, indent=2)
    last_participation_data_json = encoder.encode(last_participation_data)

    return request_render_to_response(request, "pollster/pollster_run_clean.html" if clean_template else 'pollster/pollster_run.html', {
        "language": language,
        "locale_code": locale_code,
        "survey": survey,
        "default_postal_code_format": fields.PostalCodeField.get_default_postal_code_format(),
        "last_participation_data_json": last_participation_data_json,
        "form": form
#        "person": survey_user
    })

def survey_map(request, survey_shortname, chart_shortname):
    survey = get_object_or_404(models.Survey, shortname=survey_shortname, status='PUBLISHED')
    chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname)

    global_id = request.GET.get('gid', None)
    profile = None
    if global_id:
        profile = get_user_profile(request.user.id, global_id)

    return request_render_to_response(request, 'pollster/mobile_survey_chart.html', {
        'profile': profile,
        'chart': chart,
    })

@staff_member_required
def survey_translation_list_or_add(request, id):
    function = 'def survey_translation_list_or_add'
    logger.info('%s' % function)
    survey = get_object_or_404(models.Survey, pk=id)
    form_add = forms.SurveyTranslationAddForm()
    if request.method == 'POST':
        logger.info('%s POST' % function)
        form_add = forms.SurveyTranslationAddForm(request.POST)
        if form_add.is_valid():
            logger.info('%s is_valid' % function)
            language = form_add.cleaned_data['language']
            translations = survey.translationsurvey_set.all().filter(language=language)[0:1]
            if translations:
                logger.info('%s - translations:%s' % (function, translations))
                translation = translations[0]
            else:
                logger.info('%s - create translations' % function)
                translation = models.TranslationSurvey(survey=survey, language=language)
                survey.set_translation_survey(translation)
                survey.translation_survey.save()
                for question in survey.questions:
                    question.translation_question.save()
                    for option in question.options:
                        option.translation_option.save()
                    for row in question.rows:
                        row.translation_row.save()
                    for column in question.columns:
                        column.translation_column.save()

            return redirect(translation)
    return request_render_to_response(request, 'pollster/survey_translation_list.html', {
        "survey": survey,
        "form_add": form_add
    })


@staff_member_required
def survey_translation_edit(request, id, language):
    function = 'def survey_translation_edit'
    logger.info('%s' % function)
    survey = get_object_or_404(models.Survey, pk=id)
    translation = get_object_or_404(models.TranslationSurvey, survey=survey, language=language)
    survey.set_translation_survey(translation)
    if request.method == 'POST':
        forms = []
        forms.append( survey.translation.as_form(request.POST) )
        for question in survey.questions:
            forms.append( question.translation.as_form(request.POST) )
            for row in question.rows:
                forms.append( row.translation.as_form(request.POST) )
            for column in question.columns:
                forms.append( column.translation.as_form(request.POST) )
            for option in question.options:
                forms.append( option.translation.as_form(request.POST) )
        if all(f.is_valid() for f in forms):
            for form in forms:
                form.save()
            messages.success(request, 'Translation saved successfully.')
            return redirect(translation)
    return request_render_to_response(request, 'pollster/survey_translation_edit.html', {
        "survey": survey,
        "translation": translation
    })

@staff_member_required
def survey_chart_list_or_add(request, id):
    function = 'def survey_chart_list_or_add'
    logger.info('%s' % function)
    survey = get_object_or_404(models.Survey, pk=id)
    form_add = forms.SurveyChartAddForm()
    if request.method == 'POST':
        form_add = forms.SurveyChartAddForm(request.POST)
        if form_add.is_valid():
            shortname = form_add.cleaned_data['shortname']
            charts = survey.chart_set.all().filter(shortname=shortname)[0:1]
            if charts:
                chart = charts[0]
            else:
                chart = models.Chart(survey=survey, shortname=shortname)
                chart.type = models.ChartType.objects.all().order_by('id')[0]
                chart.save()
            return redirect(chart)
    return request_render_to_response(request, 'pollster/survey_chart_list.html', {
        "survey": survey,
        "form_add": form_add
    })


@staff_member_required
def survey_chart_edit(request, id, shortname):
    function = 'def survey_chart_edit'
    logger.info('%s' % function)
    survey = get_object_or_404(models.Survey, pk=id)
    chart = get_object_or_404(models.Chart, survey=survey, shortname=shortname)
    form_chart = forms.SurveyChartEditForm(instance=chart)
    if request.method == 'POST':
        form_chart = forms.SurveyChartEditForm(request.POST, instance=chart)
        if form_chart.is_valid():
            form_chart.save()
            if not chart.update_table():
                msg = 'Unable to gather some data. Please check the SQL statements.'
                if chart.is_published:
                    messages.error(request, msg)
                else:
                    messages.warning(request, msg)
            return redirect(chart)
    return request_render_to_response(request, 'pollster/survey_chart_edit.html', {
        "survey": survey,
        "chart": chart,
        "form_chart": form_chart,
    })

@staff_member_required
def survey_chart_data(request, id, shortname):
    function = 'def survey_chart_data'
    logger.debug(function)
    logger.debug('%s - pk:%s shortname:%s' % (function, id, shortname))

    #survey = get_object_or_404(models.Survey, id=id)

    try:
        survey = models.Survey.get(pk=id)
        logger.debug('%s - survey:' % (function, survey))
    except models.Survey.DoesNotExits:
        logger.debug('%s - No existe' % function)
        raise Http404


    logger.debug('%s - aqui estamos:' % function)


    chart = get_object_or_404(models.Chart, survey=survey, shortname=shortname)
    logger.debug('%s - chart:' % (function, chart))

    survey_user = _get_active_survey_user(request)
    logger.debug('%s - survey_user:' % (function, survey_user))

    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    logger.debug('%s - global_id:' % (function, global_id))

    return HttpResponse(chart.to_json(user_id, global_id), mimetype='application/json')

@staff_member_required
def survey_chart_map_tile(request, id, shortname, z, x, y):
    if int(z) > 22:
        raise Http404
    survey = get_object_or_404(models.Survey, pk=id)
    chart = get_object_or_404(models.Chart, survey=survey, shortname=shortname)
    survey_user = _get_active_survey_user(request)
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    return HttpResponse(retry(chart.get_map_tile, user_id, global_id, int(z), int(x), int(y)), mimetype='image/png')

@staff_member_required
def survey_chart_map_click(request, id, shortname, lat, lng):
    survey = get_object_or_404(models.Survey, pk=id)
    chart = get_object_or_404(models.Chart, survey=survey, shortname=shortname)
    return HttpResponse(chart.get_map_click(float(lat), float(lng)), mimetype='application/json')

@staff_member_required
def survey_results_csv(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    now = datetime.datetime.now()
    response = HttpResponse(mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=survey-results-%d-%s.csv' % (survey.id, format(now, '%Y%m%d%H%M'))
    writer = csv.writer(response)
    survey.write_csv(writer)
    return response

def pollster_get_data(user_id,shortname,id):
    # Get data from Intake query by user
    function = 'def pollster_get_data'
    logger.info('%s: shortname:%s user_id:%s' % (function, shortname, user_id))

    if shortname == 'intake':
        logger.info('%s  Busqueda:intake' % function )
        data = models.ResultsIntake.get_by_user(user_id)
    else:
        logger.info('%s  Busqueda:monthly' % function )
        data = models.ResultsMonthly.get_by_user_id(user_id, id)

    return data

def pollster_del_data(user_id,shortname,id):
    # Get data from Intake query by user
    function = 'def pollster_del_data'
    logger.info('%s: shortname:%s user_id:%s' % (function, shortname, user_id))

    if shortname == 'intake':
        data = models.ResultsIntake.get_by_user(user_id)
    else:
        data = models.ResultsMonthly.get_by_user_id(user_id, id)

@login_required
def pollster_data(request, shortname, id=0):
    function = 'def pollster_data'
    logger.info('%s' % function)
    logger.info('%s: shortname:%s id:%s' % (function, shortname, id))

    language=None
    form = None

    survey = get_object_or_404(models.Survey, shortname=shortname)
    if language:
        translation = get_object_or_404(models.TranslationSurvey, survey=survey, language=language)
        survey.set_translation_survey(translation)
    if language is None:
        language = get_language()
    locale_code = locale.locale_alias.get(language)
    if locale_code:
        locale_code = locale_code.split('.')[0].replace('_', '-')
        if locale_code == "en-US":
            locale_code = "en-GB"

    user_id = request.user.id
    last_participation_data = None

    encoder = json.JSONEncoder(ensure_ascii=False, indent=2)
    last_participation_data_json = encoder.encode(last_participation_data)

    data = pollster_get_data(user_id,shortname, id)
    logger.error('%s: after pollster_get_data' % function)

    if data is None:
        logger.error('%s: No data' % function)
        messages.error(request, 'Unable to find data with this survey.')
        return request_render_to_response(request, 'pollster/messages.html')

    if (request.method == 'POST'):
        logger.info('%s: POST ' % function)

        # Reenvio a la funcion de update
        return HttpResponseRedirect(reverse(pollster_update, kwargs={'survey':survey}))

    else:
        template = 'pollster/pollster_data.html'
        logger.info('%s: data:' % (function))
        return request_render_to_response(request, template, {
            "language": language,
            "locale_code": locale_code,
            "survey": survey,
            "data" : data,
            "default_postal_code_format": fields.PostalCodeField.get_default_postal_code_format(),
            "last_participation_data_json": last_participation_data_json,
            "language": language,
            "form": form
        })

def survey_export_xml(request, id):
    survey = get_object_or_404(models.Survey, pk=id)
    now = datetime.datetime.now()
    response = render(request, 'pollster/survey_export.xml', { "survey": survey }, content_type='application/xml')
    response['Content-Disposition'] = 'attachment; filename=survey-export-%d-%s.xml' % (survey.id, format(now, '%Y%m%d%H%M'))
    return response

@staff_member_required
def survey_import(request):
    function = 'def survey_import'
    logger.debug(function)

    form_import = forms.SurveyImportForm()
    if request.method == 'POST':
        form_import = forms.SurveyImportForm(request.POST, request.FILES)
        if form_import.is_valid():
            xml = request.FILES['data'].read()
            survey = models.Survey()
            # create and redirect
            parser.survey_update_from_xml(survey, xml)
            return redirect(survey)
    return redirect(survey_list)

def chart_data(request, survey_shortname, chart_shortname):
    function = 'chart_data'
    #logger.debug(function)
    chart = None
    if request.user.is_active and request.user.is_staff:
        #logger.debug('%s is_staff' % function)
        survey = get_object_or_404(models.Survey, shortname=survey_shortname)
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname)
    else:
        #logger.debug('%s is_currito' % function)
        survey = get_object_or_404(models.Survey, shortname=survey_shortname, status='PUBLISHED')
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname, status='PUBLISHED')

    #logger.debug('%s - survey:%s' % (function, survey))
    #logger.debug('%s - chart:%s' % (function, chart))

    survey_user = _get_active_survey_user(request)
    #logger.debug('%s - survey_user:%s' % (function, survey_user))

    user_id = request.user.id
    #logger.debug('%s - user_id:%s' % (function, user_id))

    global_id = survey_user and survey_user.global_id
    #logger.debug('%s - global_id:%s' % (function, global_id))

    return HttpResponse(chart.to_json(user_id, global_id), mimetype='application/json')

def map_tile(request, survey_shortname, chart_shortname, z, x, y):
    function = 'def map_tile'
    #logger.debug(function)

    if int(z) > 22:
        raise Http404
    chart = None
    if request.user.is_active and request.user.is_staff:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname)
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname)
    else:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname, status='PUBLISHED')
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname, status='PUBLISHED')
    survey_user = _get_active_survey_user(request)
    user_id = request.user.id
    global_id = survey_user and survey_user.global_id
    return HttpResponse(retry(chart.get_map_tile, user_id, global_id, int(z), int(x), int(y)), mimetype='image/png')

def map_click(request, survey_shortname, chart_shortname, lat, lng):
    function = 'def map_click'
    #logger.debug(function)

    chart = None
    if request.user.is_active and request.user.is_staff:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname)
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname)
    else:
        survey = get_object_or_404(models.Survey, shortname=survey_shortname, status='PUBLISHED')
        chart = get_object_or_404(models.Chart, survey=survey, shortname=chart_shortname, status='PUBLISHED')
    return HttpResponse(chart.get_map_click(float(lat), float(lng)), mimetype='application/json')

# based on http://djangosnippets.org/snippets/2059/

def urls(request, prefix=''):
    """
        Returns javascript for mapping service endpoint names to urls.

        For this view to work properly, all urls that are to be made
        available and are using regular expressions for defining
        parameters must use named parameters.

        The view uses Django internal url resolver to iterate over a list
        of all currently defined url patterns.  It looks for named patterns
        and replaces each named regex group definition the group name enclosed
        in curley braces.  Url pattern names will be translated into
        javascript variable names by converting all letters to the upper
        case and replacing '-' with '_'.
        """
    resolver = get_resolver(None)

    urls = {}

    for name in resolver.reverse_dict:
        if isinstance(name, str) and name.startswith(prefix):
            url_regex = resolver.reverse_dict.get(name)[1]
            param_names = resolver.reverse_dict.get(name)[0][0][1]
            arg_pattern = r'\(\?P\<[^\)]+\)'  #matches named groups in the form of (?P<name>pattern)

            i = 0
            for match in re.findall(arg_pattern, url_regex):
                url_regex = url_regex.replace(match, "{%s}"%param_names[i])
                i += 1

            urls[name] = "/" + url_regex[:-1]

    return request_render_to_response(request, "pollster/urls.js", {'urls':urls}, mimetype="application/javascript")

def _get_active_survey_user(request):
    function = 'def get_active_survey_user'
    logger.debug(function)

    gid = request.GET.get('gid', None)
    if gid is None or not request.user.is_active:
        return None
    else:
        return get_object_or_404(SurveyUser, global_id=gid, user=request.user)

def _get_next_url(request, default):
    function = 'def get_next_url'
    logger.debug(function)

    url = request.GET.get('next', default)
    survey_user = _get_active_survey_user(request)
    if survey_user:
        url = '%s?gid=%s' % (url, survey_user.global_id)
    return url

