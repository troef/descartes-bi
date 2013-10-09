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

    def process_data(self):
        series_results = self.report.execute()

        serie = []

        #TODO: Improve
        for series_result in series_results:
            for i in series_result:
                for k, v in i.iteritems():
                    serie.append({"x": k, "y": v})

        series_chart_data = [{"values": serie}]

        return series_chart_data

    def render(self, request):
        #TODO: Error handling
        context = {
            'series_results': """%s;\n""" % json.dumps(self.process_data()),
            'id': report.id,
            'chart_options': chart_options,
            'report': self.report,
        }

        logger.debug('context: %s' % context)

        #Select template. Default to standard bar chart.
        page = self.chart_template.get(self.chart_options.get('chart','SI'))

        return render_to_response(page, context, context_instance=RequestContext(request))
