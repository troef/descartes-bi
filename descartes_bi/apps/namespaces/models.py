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

from django.db import models
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey

from dashboards.models import Dashboard
from reports.models import Menuitem
from website.models import Website

TYPE_MENU = 1
TYPE_DASHBOARD = 2
TYPE_WEBSITES = 3

TYPE_CHOICES = (
    (TYPE_MENU, _('Menus')),
    (TYPE_DASHBOARD, _('Dashboard')),
    (TYPE_WEBSITES, _('Websites')),
)

class Namespace(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True, related_name='children')
    label = models.CharField(max_length=32)
    icon = models.CharField(max_length=32)
    view_type = models.PositiveIntegerField(choices=TYPE_CHOICES, null=True, blank=True)
    view_menu = models.ManyToManyField(Menuitem, null=True, blank=True, verbose_name=_('menu item'), related_name='menus')
    view_dash = models.ForeignKey(Dashboard, null=True, blank=True, verbose_name=_('dashboard item'), related_name='dashboard')
    view_website = models.ManyToManyField(Website, null=True, blank=True, verbose_name=_('website item'), related_name='websites')

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return reverse('node_view', args=[str(self.pk)])

    class MPTTMeta:
        verbose_name = 'namespace'
        verbose_name_plural = _('namespaces')
