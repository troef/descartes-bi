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
from django.utils.translation import ugettext_lazy as _

from mptt.models import MPTTModel, TreeForeignKey

from dashboard.models import Dash
from reports.models import Menuitem

TYPE_MENU = 1
TYPE_WIDGETS = 2

TYPE_CHOICES = (
    (TYPE_MENU, _('Menus')),
    (TYPE_WIDGETS, _('Dashboard')),
)


class Namespace(MPTTModel):
    parent = TreeForeignKey('self', null=True, blank=True,
        related_name='children')
    label = models.CharField(max_length=32)
    icon = models.CharField(max_length=32)
    view_type = models.PositiveIntegerField(choices=TYPE_CHOICES, blank=True,
        null=True)
    view_menu = models.ManyToManyField(Menuitem, null=True, blank=True,
        verbose_name=_('menu item'))
    view_dash = models.ManyToManyField(Dash, null=True, blank=True,
        verbose_name=_('dash item'))

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = _('namespace')
        verbose_name_plural = _('namespaces')
