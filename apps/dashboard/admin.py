from django.contrib import admin

from dashboard.models import Dash


class DashAdmin(admin.ModelAdmin):
    filter_horizontal = ('selection_list',)


admin.site.register(Dash, DashAdmin)
