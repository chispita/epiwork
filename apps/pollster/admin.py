from django.contrib import admin
from .models import RuleType, QuestionDataType, VirtualOptionType, Survey, TranslationSurvey, Chart, ResultsIntake

#Results_Intake, Results_Monthly

class ResultsIntake_Admin(admin.ModelAdmin):
    #list_display = ('id', 'user.name', 'timestamp')
    search_fields = ['id']

class Results_Monthly_Admin(admin.ModelAdmin):
    #list_display = ('id','surveruser','timestamp')
    list_display = ('id','timestamp')

admin.site.register(RuleType)
admin.site.register(QuestionDataType)
admin.site.register(VirtualOptionType)
admin.site.register(Survey)
admin.site.register(TranslationSurvey)
admin.site.register(Chart)
admin.site.register(ResultsIntake)
#admin.site.register(Results_Monthly, Results_Monthly_Admin)
