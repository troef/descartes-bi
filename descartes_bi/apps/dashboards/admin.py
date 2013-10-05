from __future__ import absolute_import

from django.contrib import admin

from .models import Dashboard, DashboardElement


class DashboardElementInline(admin.StackedInline):
    model = DashboardElement
    extra = 1
    radio_fields = {'visual_type': admin.HORIZONTAL}


class DashboardAdmin(admin.ModelAdmin):
    inlines = [DashboardElementInline]


admin.site.register(Dashboard, DashboardAdmin)
