from __future__ import absolute_import

from django.utils.translation import ugettext_lazy as _

from .base import ChartBackend


class NovusD3(ChartBackend):
    label = _('Novus D3')

    CHART_TYPE_CHOICES = (
        ('SI', _('Standard X,Y')),
        ('SH', _('Horizontal X,Y')),
        ('PI', _('Pie chart')),
        ('LB', _('Line Plus Bar Chart')),
        ('LI', _('Line chart')),
        ('LF', _('Line chart with Focus')),
    )
