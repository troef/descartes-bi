from __future__ import absolute_import

import json
import logging

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext_lazy as _

from .base import ChartBackend

logger = logging.getLogger(__name__)


class NovusD3(ChartBackend):
    label = _('Novus D3')

    options = [
        {
            'name': 'chart_type',
            'label': _('chart type'),
            'choices': (
                ('SI', _('Standard X,Y')),
                ('SH', _('Horizontal X,Y')),
                ('PI', _('Pie chart')),
                ('LB', _('Line Plus Bar Chart')),
                ('LI', _('Line chart')),
                ('LF', _('Line chart with Focus')),
            )
        },
        {
            'name': 'chart_options',
            'label': _('chart options'),
        }
    ]

    chart_template = {
        'SI': 'charts/novus/multiBarChart.html',  # 'Standard X,Y'
        'LI': 'charts/novus/lineChart.html',  # Line chart
        'PI': 'charts/novus/pieChart.html',  # Pie chart
    }

    def process_data(self, series_results):

        series = []

        for serie in series_results:
            for k, v in serie.iteritems():
                series.append(dict(x=k, y=v))

        return series

    def render(self, request):

        # Get data
        series_results = self.report.execute(request)
        # chart_options = report.renderer_options

        chart_data = []

        for result in series_results:
            chart_data.append([dict(values=self.process_data(result['results'])),
                               dict(key=result['report_series'].series.label)])

        #TODO: Error handling
        context = {
            'series_results': """%s;\n""" % json.dumps(chart_data),
            #'chart_options': chart_options,
            'report': self.report,
        }

        logger.debug('context: %s' % context)

        #Select template.
        page = self.chart_template.get('LI')

        return render_to_response(page, context, context_instance=RequestContext(request))
