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

from dashboard.models import Dash
from website.views import get_website

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

    page = 'namespaces/node.html'

    if node:
        #view_type 1 - Menu, view_type 2 - Dashboard
        if node.view_type == 1:
            context['menus'] = node.view_menu.all()
            #page = 'sub_dash_menu.html'
        elif node.view_type == 2:
            dash_board = get_object_or_404(Dash, pk=node.view_dash_id)
            selected_reports = dash_board.selection_list.all()
            links = {}
            for sp in selected_reports:
                if sp.rep_id:
                    get_form = ""
                    if sp.filtersets:
                        filterform = sp.filtersets.filters.all()
                        values = sp.values.split(',')
                        for index in range(len(values)):
                            get_form += filterform[index].name + "=" + values[index] + "&"

                    lk = reverse('reports:ajax_report_view', args=[sp.rep_id.id])# + "/?" + get_form + "output_type=" + sp.visual_type
                    links[str(sp.id)] = lk
                if sp.website:
                    query = sp.website.series.query
                    if sp.website.filterset.exists():
                        filterform = sp.filtersets.filters.all()
                        values = sp.values.split(',')
                        dic = {}
                        for index in range(len(values)):
                            if values[index].isdigit():
                                dic[filterform[index].name] = int(values[index])
                            else:
                                dic[filterform[index].name] = values[index]
                        query = query % dic
                    if sp.website.base_URL:
                        links["mapdiv" + str(sp.id)] = sp.website.base_URL + "/?" + query
                    else:
                        links["mapdiv" + str(sp.id)] = sp.website.series.data_source.load_backend().cursor().url + "/?" + query
            context = {'selected_reports': selected_reports,
                       'dash_board': dash_board, 'links': links}
            page = 'dashboard/dash_list.html'

        #Check if the view_type is a website and call the website view
        elif node.view_type == 3:
            website = node.view_website.all()[0]
            return get_website(request, website)


    """
    if node:
        if node.is_leaf_node():
            #view_type 1 - Menu, view_type 2 - Dashboard
            if node.view_type == 1:
                context['menus'] = node.view_menu.all()
                page = 'sub_dash_menu.html'



            elif node.view_type == 2:
                dash_id = node.view_dash_id
                dash_board = get_object_or_404(Dash, pk=dash_id)
                selected_reports = dash_board.selection_list.all()
                links = {}
                for sp in selected_reports:
                    if sp.rep_id:
                        get_form = ""
                        if sp.filtersets:
                            filterform = sp.filtersets.filters.all()
                            values = sp.values.split(',')
                            for index in range(len(values)):
                                get_form += filterform[index].name + "=" + values[index] + "&"

                        lk = "reports/ajax/report/" + str(sp.rep_id.id) + "/?" + get_form + "output_type=" + sp.visual_type
                        links[str(sp.id)] = lk
                    if sp.website:
                        query = sp.website.series.query
                        if sp.website.filterset.exists():
                            filterform = sp.filtersets.filters.all()
                            values = sp.values.split(',')
                            dic = {}
                            for index in range(len(values)):
                                if values[index].isdigit():
                                    dic[filterform[index].name] = int(values[index])
                                else:
                                    dic[filterform[index].name] = values[index]
                            query = query % dic
                        if sp.website.base_URL:
                            links["mapdiv" + str(sp.id)] = sp.website.base_URL + "/?" + query
                        else:
                            links["mapdiv" + str(sp.id)] = sp.website.series.data_source.load_backend().cursor().url + "/?" + query
                context = {'selected_reports': selected_reports,
                           'dash_board': dash_board, 'links': links}
                page = 'dashboard/dash_list.html'

            else:
                page = 'sub_dash_menu.html'
        else:
            context['nodes'] = node.get_children()
            page = 'sub_dash_menu.html'
    """

    return render_to_response(page, context,
        context_instance=RequestContext(request))
