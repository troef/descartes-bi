from __future__ import absolute_import

import logging

from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from .models import Dashboard

logger = logging.getLogger(__name__)


def dashboard_view(request, dashboard_pk):
    dashboard = get_object_or_404(Dashboard, pk=dashboard_pk)

    context = {'dashboard': dashboard, 'elements': dashboard.elements.filter(enabled=True)}
    return render(request, 'dashboards/dashboard.html', context)
