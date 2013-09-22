from __future__ import absolute_import

from django.contrib.auth.models import User
from django.db import connections
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
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

    def render(self, report, request):

        series_results = report.execute(request)

        context = {
            'series_results': series_results,
            'ajax': True,
            'report': report,
        }

        #print 'series_results', series_results

        #return HttpResponse("asd")
        #if output_type == 'chart':
        return render_to_response('single_chart.html', context,
            context_instance=RequestContext(request))
        #elif output_type == 'grid':
        #    return render_to_response('single_grid.html', data,
        #        context_instance=RequestContext(request))
        #else:
        #    return render_to_response('messagebox-error.html', {'title': _(u'Error'), 'message': _(u"Unknown output type (chart, table, etc).")})
