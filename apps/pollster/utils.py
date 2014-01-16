from . import models
from django.conf import settings

import logging
logger = logging.getLogger(__name__)

def get_user_profile(user_id, global_id):
    function ='def get_user_profile'
    logger.info(function)
    logger.info('%s - user_id:%s, global_id:%s' % (function, user_id,global_id))

    try:
        shortname = getattr(settings, 'POLLSTER_USER_PROFILE_SURVEY', 'intake')
        logger.info('%s - shortname:%s' % (function, shortname))

        survey = models.Survey.get_by_shortname(shortname)

        profile = survey.get_last_participation_data(user_id, global_id)

        return profile
    except models.Survey.DoesNotExist:
        logger.info('%s - Survey.DoesNotExit' % function)
        return None
    except StandardError, e:
        return None
