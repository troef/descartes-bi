from __future__ import absolute_import

#
#    Copyright (C) 2010  Roberto Rosario
#    This file is part of descartes-bi.
#
#    descartes-bi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    descartes-bi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with descartes-bi.  If not, see <http://www.gnu.org/licenses/>.
#
import datetime
import logging
import json
import re

from django.db import connections
from django.http import HttpResponse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.utils.translation import ugettext as _

from db_drivers.models import BACKEND_LIBRE
from main.exceptions import SeriesError

from .forms import FilterForm
from .models import Report, Menuitem, GroupPermission, UserPermission, User, SeriesStatistic, ReportStatistic
from .literals import FILTER_TYPE_DATE, FILTER_TYPE_COMBO
from .utils import get_allowed_object_for_user


logger = logging.getLogger(__name__)


def ajax_filter_form(request, report_id):
    #TODO: access control
    if request.method == 'GET':
        query = request.GET

    report = get_object_or_404(Report, pk=report_id)

    if report not in get_allowed_object_for_user(request.user)['reports']:
        return render_to_response('messagebox-error.html',
                                  {'title': _(u'Permission error'),
                                   'message': _(u"Insufficient permissions to access this area.")})

    if query:
        filter_form = FilterForm(report.filtersets.all(), request.user, query)
    else:
        filter_form = FilterForm(report.filtersets.all(), request.user)

    return render_to_response('filter_form_subtemplate.html', {'filter_form': filter_form},
        context_instance=RequestContext(request))


def ajax_report_description(request, report_id):
    report = get_object_or_404(Report, pk=report_id)

    result = "<strong>%s</strong><br />%s" % (report.title, report.description or '')
    return HttpResponse(result)


def ajax_report_validation(request, report_id):
    report = get_object_or_404(Report, pk=report_id)

    result = ''

    for s in report.series.all():
        if s.validated:

            result += "<li>'%s' validated on %s" % (s.label or unicode(s),
                                                    s.validated_date)
            if s.validated_person:
                result += " by %s" % s.validated_person
            result += '</li><br />'

    if result:
        return HttpResponse('<ul>%s</ul>' % result)
    else:
        return HttpResponse(_(u'No element of this report has been validates.'))


def ajax_report(request, report_id):
    start_time = datetime.datetime.now()

    report = get_object_or_404(Report, pk=report_id)

    if report not in get_allowed_object_for_user(request.user)['reports']:
        return render_to_response('messagebox-error.html',
         {'title': _(u'Permission error'),
          'message': _(u"Insufficient permissions to access this area.")})

    output_type = request.GET.get('output_type', 'chart')
    params = {}
    special_params = {}

    if report.filtersets.all():
        filtersets = report.filtersets
        if request.method == 'GET':
            filter_form = FilterForm(filtersets, request.user, request.GET)
        else:
            filter_form = FilterForm(filtersets, request.user)

        for set in filtersets.all():
            for filter in set.filters.all():

                if filter_form.is_valid():
                    value = filter_form.cleaned_data[filter.name]
                    if not value:
                        filter.execute_function()
                        value = filter.default

                else:
                    filter.execute_function()
                    value = filter.default

                if filter.type == FILTER_TYPE_DATE:
                    params[filter.name] = value.strftime("%Y%m%d")
                elif filter.type == FILTER_TYPE_COMBO:
                    special_params[filter.name] = '(' + ((''.join(['%s'] * len(value)) % tuple(value))) + ')'
                else:
                    params[filter.name] = value

    try:
        series_results = report.execute(params, special_params, output_type)
    except SeriesError as exception:
        return render_to_response('messagebox-error.html', {'title': _('Series error'), 'message': exception})

    #data = {
    #    'backend_libre': BACKEND_LIBRE,
    #    'series_results': series_results,
    #    'report_series': report.report_series.all(),
    #    'ajax': True,
    #    'report': report,
    #}

    ##if output_type == 'chart':
    # #   return render_to_response('single_chart.html', data,
    #        context_instance=RequestContext(request))
    #elif output_type == 'grid':
    #    return render_to_response('single_grid.html', data,
    #        context_instance=RequestContext(request))
    #else:
    #    return render_to_response('messagebox-error.html', {'title': _(u'Error'), 'message': _(u"Unknown output type (chart, table, etc).")})
