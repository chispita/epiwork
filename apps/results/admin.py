from django.contrib import admin
from .models import Intake

admin.site.register(Intake)

class IntakeAdmin(admin.ModelAdmin):
    list_display = ('id', 'global_id')

admin.site.register(Intake, IntakeAdmin)
