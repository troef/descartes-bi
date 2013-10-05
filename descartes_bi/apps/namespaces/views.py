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
import logging
import os
import re

from django import http
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import loader, RequestContext

from dashboards.models import Dashboard
from dashboards.views import dashboard_view
from website.views import website_view

from .models import Namespace

logger = logging.getLogger(__name__)


def node_view(request, node_pk=None):
    if node_pk:
        node = get_object_or_404(Namespace, pk=node_pk)
        child_nodes = node.get_children()
    else:
        child_nodes = [node for node in Namespace.objects.all() if node.is_root_node()]
        node = None

    logger.debug('node_pk: %s' % node_pk)
    logger.debug('node: %s' % node)
    logger.debug('child_nodes: %s' % child_nodes)

    context = {
        'node': node,
        'child_nodes': child_nodes,
    }

    if node:
        #view_type 1 - Menu, view_type 2 - Dashboard
        if node.view_type == 1:
            context['menus'] = node.view_menu.all()
        elif node.view_type == 2:
            dashboard = get_object_or_404(Dashboard, pk=node.view_dash_id)
            return dashboard_view(request, dashboard.pk)
        #Check if the view_type is a website and call the website view
        elif node.view_type == 3:
            website = node.view_website.all()[0]
            return website_view(request, website.pk)

    return render_to_response('namespaces/node.html', context,
        context_instance=RequestContext(request))
