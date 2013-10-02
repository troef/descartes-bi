import logging

from django.core.urlresolvers import reverse
from django.shortcuts import render, get_object_or_404

from dashboard.models import Dash

logger = logging.getLogger(__name__)


def display(request, dash_id):
    dash_board = get_object_or_404(Dash, pk=dash_id)
    selected_reports = dash_board.selection_list.all()

    links = {}
    logger.debug('Create Links list')

    for sp in selected_reports:
        links.append(reverse('reports:ajax_report_view', args=[sp.rep_id.id]))

    logger.debug('links: %s' % links)

    context = {'selected_reports': selected_reports, 'dash_board': dash_board, 'links': links}
    return render(request, 'dashboard/dash_list.html', context)
