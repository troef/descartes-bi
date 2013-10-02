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

from django.contrib import admin
from mptt.admin import MPTTModelAdmin

from .models import Namespace
from .forms import NamespaceForm


class NamespaceAdmin(MPTTModelAdmin):
    form = NamespaceForm
    list_display = ('label', 'parent', 'icon', 'view_type')
    filter_horizontal = ('view_menu', 'view_website')
    radio_fields = {'view_type': admin.HORIZONTAL}

admin.site.register(Namespace, NamespaceAdmin)