from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import ContractThreshold, LogisticaConfiguration


@admin.register(LogisticaConfiguration)
class LogisticaConfigurationAdmin(SingletonModelAdmin):
    pass


@admin.register(ContractThreshold)
class ContractThresholdAdmin(admin.ModelAdmin):
    list_display = ("solar_system", "title", "match_type", "minimum_count")
    list_filter = ("match_type",)
    search_fields = ("title", "solar_system__name")
    autocomplete_fields = ("solar_system",)
    ordering = ("solar_system__name", "title")
