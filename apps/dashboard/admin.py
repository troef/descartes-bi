from django.contrib import admin
from dashboard.models import Dash, Selected_report


class SelectInline(admin.TabularInline):
    model = Dash.selection_list.through


class DashAdmin(admin.ModelAdmin):
    fieldsets = [('Name', {'fields': ['name']})]
    inlines = [SelectInline]

admin.site.register(Dash, DashAdmin)
admin.site.register(Selected_report)