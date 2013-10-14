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
        chart_type = chart_options.get('chart','SI')

        serie = []
        for s in self.report.execute():
            for k, v in s.iteritems():
                serie.append({"x": k, "y": v})

        if chart_type == 'PI':
            return serie
        else:
            series_chart_data = {"values": serie}

       series_chart_data = []

        # Get chart type, default to bar chart

        for serie_result in series_results:
            if not chart_type == 'PI':
                series_chart_data.append(self.process_data(serie_result, chart_type))
            else:
                series_chart_data = self.process_data(serie_result, chart_type)

        return series_chart_data


    def render(self, request):
        #TODO: Error handling
        context = {
            'series_results': """%s;\n""" % json.dumps(self.process_data()),
            'chart_options': chart_options,
            'report': self.report,
        }

        logger.debug('context: %s' % context)

        #Select template.
        page = self.chart_template.get(chart_type)

        return render_to_response(page, context, context_instance=RequestContext(request))
