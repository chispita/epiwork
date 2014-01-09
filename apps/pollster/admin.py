from django.contrib import admin
from django.contrib.auth.models import User
from .models import RuleType, QuestionDataType, VirtualOptionType, Survey, TranslationSurvey, Chart, ResultsIntake, ResultsMonthly

class ResultsIntake_Admin(admin.ModelAdmin):
    list_display = ('id','user', 'timestamp')
    search_fields = ['id']

class ResultsMonthly_Admin(admin.ModelAdmin):
    list_display = ('id','user','timestamp')
    #list_display = ('id','timestamp')

admin.site.register(RuleType)
admin.site.register(QuestionDataType)
admin.site.register(VirtualOptionType)
admin.site.register(Survey)
admin.site.register(TranslationSurvey)
admin.site.register(Chart)
admin.site.register(ResultsIntake, ResultsIntake_Admin)
admin.site.register(ResultsMonthly, ResultsMonthly_Admin)
