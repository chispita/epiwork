from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, render
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings

from .models import UserReminderInfo, get_upcoming_dates, get_prev_reminder, get_settings, get_default_for_reminder, NewsLetter
from .send import create_message, send, send_reminders

import logging
logger = logging.getLogger('logview.userlogins')

@login_required
def latest_newsletter(request):
    # Show the latest newsletter published
    now = datetime.now()
    newsletter_queryset = NewsLetter.objects.filter(date__lte=now, published=True).order_by("-date")
    if newsletter_queryset.count():
        latest_newsletter = newsletter_queryset.all()[0]

        info, _ = UserReminderInfo.objects.get_or_create(user=request.user, defaults={'active': True, 'last_reminder': request.user.date_joined})
        language = info.get_language()
        message, outer_message = create_message(request.user, latest_newsletter, language)
        #inner, message = create_message(request.user, latest_newsletter, language)

    return render_to_response('reminder/latest_newsletter.html', locals(), context_instance=RequestContext(request))

@login_required
def unsubscribe(request):
    if request.method == "POST":
        info, _ = UserReminderInfo.objects.get_or_create(user=request.user, defaults={'active': True, 'last_reminder': request.user.date_joined})
        info.active = False
        info.save()
        return render_to_response('reminder/unsubscribe_successful.html', locals(), context_instance=RequestContext(request))
    return render_to_response('reminder/unsubscribe.html', locals(), context_instance=RequestContext(request))

@staff_member_required
def overview(request):
    upcoming = [{
        'date': d,
        'description': description,
    } for d, description in get_upcoming_dates(datetime.now())]

    return render(request, 'reminder/overview.html', locals())

@staff_member_required
def manage(request, year, month, day, hour, minute,send=""):
    function = 'def manage'
    logger.debug(function)
    reminder_dict = get_prev_reminder(datetime(*map(int, [year, month, day, hour, minute, 59])), published=False)
    if not reminder_dict:
        return HttpResponse("There are no newsletters or reminders configured yet. Make sure to do so")

    reminder = _reminder(reminder_dict, request.user)
    if not reminder:
        return HttpResponse("There is no reminder in your current language configured. Make sure to add a translation")

    is_test_message = (send != "Send")

    if request.method == "POST":
        logger.debug('%s POST' % function)

        if is_test_message:
            logger.debug('%s POST is_test_message:%s' % (function, is_test_message))
            send(datetime.now(), request.user, reminder, None, True)
        else:
            logger.debug('%s POST is_test_message:%s' % (function, is_test_message))
            send_reminders()

    return render(request, 'reminder/manage.html', locals())


@staff_member_required
def preview(request, year, month, day, hour, minute):
    reminder_dict = get_prev_reminder(datetime(*map(int, [year, month, day, hour, minute, 59])), published=False)
    if not reminder_dict:
        return HttpResponse("There are no newsletters or reminders configured yet. Make sure to do so")

    reminder = _reminder(reminder_dict, request.user)
    if not reminder:
        return HttpResponse("There is no reminder in your current language configured. Make sure to add a translation")

    text_base, html_content = create_message(request.user, reminder, settings.LANGUAGE_CODE)
    return HttpResponse(html_content)

def _reminder(reminder_dict, user):
    info, _ = UserReminderInfo.objects.get_or_create(user=user, defaults={'active': True, 'last_reminder': user.date_joined})
    language = info.get_language()

    if not language in reminder_dict:
        language = settings.LANGUAGE_CODE
    if not language in reminder_dict:
        return None

    reminder = reminder_dict[language]

    return reminder
