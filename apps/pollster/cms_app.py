from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from django.utils.translation import ugettext_lazy as _

class SurveyIntakehook(CMSApp):
    name = _("Intake")
    urls = ["apps.pollster.urls"]
    
apphook_pool.register(SurveyIntakehook)
