from __future__ import absolute_import

import logging

from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from .models import Dashboard

logger = logging.getLogger(__name__)


def dashboard_view(request, dashboard_pk, extra_context=None):
    dashboard = get_object_or_404(Dashboard, pk=dashboard_pk)

    rows = []
    row = []
    spans = 0
    for element in dashboard.active_elements():
        spans += element.span
        if spans > 12:
            rows.append(row)
            spans = element.span
            row = []

        row.append(element)

    if row:
        rows.append(row)

    context = {'dashboard': dashboard, 'rows': rows, 'query_string': request.META['QUERY_STRING']}

    if extra_context:
        context.update(extra_context)

    return render_to_response('dashboards/dashboard.html', context,
        context_instance=RequestContext(request))
