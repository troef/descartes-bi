from __future__ import absolute_import

import logging

from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from .models import Dashboard

logger = logging.getLogger(__name__)


def dashboard_view(request, dashboard_pk, extra_context=None):
    dashboard = get_object_or_404(Dashboard, pk=dashboard_pk)

    rows = []
    row = []
    spans = 0
    for element in dashboard.active_elements():
        spans += element.span
        if spans <= 12:
            row.append(element)
        else:
            rows.append(row)
            spans = element.span
            row = [element]

    if row:
        rows.append(row)

    context = {'dashboard': dashboard, 'rows': rows}

    if extra_context:
        context.update(extra_context)

    return render(request, 'dashboards/dashboard.html', context)
