from django.contrib import admin
from dashboard.models import dash, selected_report

class SelectInline(admin.TabularInline):
    model = dash.selection_list.through

class DashAdmin(admin.ModelAdmin):
	fieldsets = [('Name', {'fields': ['name']})]
	inlines = [SelectInline]

admin.site.register(dash, DashAdmin)
admin.site.register(selected_report)