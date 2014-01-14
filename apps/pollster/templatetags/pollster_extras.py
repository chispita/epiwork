from django import template
register = template.Library()

#import re
#from django import template
#from django.conf import settings
#
#numeric_test = re.compile("^\d+$")
#register = template.Library()

#def getattribute(value, arg):
#    """Gets an attribute of an object dynamically from a string name"""
#
#    if hasattr(value, str(arg)):
#        return getattr(value, arg)
#    elif hasattr(value, 'has_key') and value.has_key(arg):
#        return value[arg]
#    elif numeric_test.match(str(arg)) and len(value) > int(arg):
#        return value[int(arg)]
#    else:
#        return settings.TEMPLATE_STRING_IF_INVALID

#register.filter('getattribute', getattribute)

@register.filter
def item( value, arg):
    # Get value from database field name
    try:
        return getattr(value, arg)
    except:
        return ''

@register.filter
def extrae(value, arg):
   # Force convertion to string 
    comp = '%s' % arg
    dst = ''

    for item in value:
        if item.value == comp:
            dst += item.text

    return dst

@register.filter
def add(value, arg):
    # Add strings
    return "%s%s" % (value, arg)

@register.filter
def add_underscore(value,arg):
    # Add strings with a underscore between
    return "%s_%s" % (value, arg)

