from cms.plugin_base import CMSPluginBase
from cms.models.pluginmodel import CMSPlugin
from cms.plugin_pool import plugin_pool
from .models import SurveyChartPlugin, SurveyChartIntake, ResultsIntake
from .utils import get_user_profile, get_energy_requests, get_energy_tips
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

import logging
logger = logging.getLogger('logview.userlogins')


class CMSSurveyChartPlugin(CMSPluginBase):
    model = SurveyChartPlugin
    name = _("Survey Chart")
    render_template = "pollster/cms_survey_chart.html"

    def render(self, context, instance, placeholder):
        request = context['request']
        global_id = request.GET.get('gid', None)
        profile = None
        if global_id:
            profile = get_user_profile(request.user.id, global_id)
        context.update({
            'profile': profile,
            'chart': instance.chart,
            'object': instance,
            'placeholder': placeholder
        })
        return context

plugin_pool.register_plugin(CMSSurveyChartPlugin)

class CMSSurveyChartIntake(CMSPluginBase):
    model = SurveyChartIntake
    name = _("Survey Chart Intake")
    render_template = "pollster/cms_survey_chart_intake.html"

    def render(self, context, instance, placeholder):
        request = context['request']

        context.update({
            'object':instance,
            'chart': instance,
            'placeholder':placeholder
        })
        return context

plugin_pool.register_plugin(CMSSurveyChartIntake)

# Plugin to display request for energy consumption at home, 
# according to home characteristics inserted by the user. 
# energy_calc_plugin.html render the template
class energyCalcPlugin(CMSPluginBase):
    name= _("energyCalcPlugin")
    model = CMSPlugin
    render_template = "energyCalc_plugin.html"

    # Prepare the context for the template
    # Pre: context is the current context
    #      instance, placeholder not null
    # Post: Updated context
    def render(self, context, instance, placeholder):

    	# Debug
	function ='class energyCalcPlugin'
    	logger.debug(function)
        
	# Retrieves request from the context in order to get the user id
	request = context['request']

	# Debug
     	logger.debug('%s - Request Id:%s' % (function,request.user.id))

	# Retrieves intake surveys from the database
	survey_intake = ResultsIntake.objects.all().filter(user=request.user)
	
	if survey_intake:
		# User has filled in intake survey
		
		# Debug
     		logger.debug('%s - survey:%s' % (function,survey_intake))

		# Saves in an attribute of the context (in order to pass them to the
		# template) the calculated energy requests for the home
		context['energy_requests'] = get_energy_requests(survey_intake[0])

	else:
		# User has not filled in intake survey

		# Debug
		logger.debug('%s - Intake not filled in' % function)
		
		# Return energy_requests as zero
		context['energy_requests'] = 0
	
	# Return the context with the addition of the estimated energy requests
	# for being displayed in the template
        context['instance'] = instance
        return context

# Register the plugin
plugin_pool.register_plugin(energyCalcPlugin)

# Plugin to display tips for energy consumption at home, 
# according to home characteristics inserted by the user. 
# tips_plugin.html render the template
class tipsPlugin(CMSPluginBase):
    name= _("tipsPlugin")
    model = CMSPlugin
    render_template = "tips_plugin.html"

    # Prepare the context for the template
    # Pre: context is the current context
    #      instance, placeholder not null
    # Post: Updated context
    def render(self, context, instance, placeholder):

        # Debug
        function ='class tipsPlugin'
        logger.debug(function)

        # Retrieves request from the context in order to get the user id
        request = context['request']

        # Debug
        logger.debug('%s - Request Id:%s' % (function,request.user.id))

        # Retrieves intake surveys from the database
        survey_intake = ResultsIntake.objects.all().filter(user=request.user)

        if survey_intake:
                # User has filled in intake survey

                # Debug
                logger.debug('%s - survey:%s' % (function,survey_intake))

                # Saves in an attribute of the context (in order to pass them to the
                # template) the tips for the home
                context['energy_tips'] = get_energy_tips(survey_intake[0])

        else:
                # User has not filled in intake survey

                # Debug
                logger.debug('%s - Intake not filled in' % function)

                # Return energy_requests as zero
                context['energy_tips'] = 0

        # Return the context with the addition of the energy tips
        # for being displayed in the template
        context['instance'] = instance
        return context

# Register the plugin
plugin_pool.register_plugin(tipsPlugin)

class CMSSurveyResults(CMSPluginBase):
    model = SurveyChartIntake
    name = _("Survey Results  Intake")

    def render(self, context, instance, placeholder):
        request = context['request']

        reversed_url = reverse('survey:thanks_profile',
           current_app=context.current_app)


plugin_pool.register_plugin(CMSSurveyResults)

