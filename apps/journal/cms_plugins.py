from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool

from .models import LatestEntryPlugin, Entry, published_filter
from . import settings

import logging
logger = logging.getLogger('logview.userlogins')  #

class CMSLatestEntryPlugin(CMSPluginBase):
    """
        Plugin class for the latest news
    """
    function = "def CMSLatestEntryPlugin"
    logger.debug(function)

    model = LatestEntryPlugin
    name = _('Journal entries')
    render_template = "journal/latest.html"

    def render(self, context, instance, placeholder):
        """
            Render the latest news
        """
        function = "def CMSLatestEntryPlugin"
        logger.debug('%s - render' % function)
        categories = instance.category.all()
        if len(categories) > 0:
            logger.debug('%s - categories:%s' % (function, categories))
            query = map(lambda category: Q(category=category),
                        categories)

            logger.debug('%s - categories:%s' % (function, query))
            query = reduce(lambda a, b: a | b, query)
            logger.debug('%s - categories:%s' % (function, query))
        else:
            query = Q()
            logger.debug('%s - 0 categories:%s' % (function, query))
        latest = published_filter(Entry.objects.filter(query)).order_by("-pub_date")[:instance.limit]
        logger.debug('%s - latest:%s' % (function, latest))

        context.update({
            'title': instance.title,
            'instance': instance,
            'latest': latest,
            'placeholder': placeholder,
        })
        return context

if not settings.DISABLE_LATEST_ENTRIES_PLUGIN:
    plugin_pool.register_plugin(CMSLatestEntryPlugin)
