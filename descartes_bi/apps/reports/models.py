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
from multiprocessing import Pipe, Process
import re

from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.db import models
from django.utils.translation import ugettext_lazy as _

from charts.literals import BACKEND_CHOICES
from charts.utils import import_backend
from db_drivers.models import DataSource

from .exceptions import SeriesError
from .forms import FilterForm
from .literals import FILTER_FIELD_CHOICES, SERIES_TYPE_CHOICES, UNION_CHOICES, FILTER_TYPE_DATE, FILTER_TYPE_COMBO


logger = logging.getLogger(__name__)


class Filter(models.Model):
    name = models.CharField(max_length=48, help_text=_('Name of the parameter to be used in the queries.  Do not use spaces or special symbols.'), verbose_name=_('name'))
    description = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('description'))
    type = models.CharField(max_length=2, choices=FILTER_FIELD_CHOICES, verbose_name=_('type'))
    label = models.CharField(max_length=32, help_text='Text label that will be presented to the user.', verbose_name=_('label'))
    default = models.CharField(max_length=32, blank=True, null=True, help_text='Defautl value or one the special functions [this_day, this_month, this_year].', verbose_name=_('default'))
    options = models.TextField(blank=True, null=True, verbose_name=_('options'))

    def __unicode__(self):
        if self.description:
            return '%s "%s"' % (self.name, self.description)
        else:
            return self.name

    def get_parents(self):
        return ', '.join(['"%s"' % p.name for p in self.filterset_set.all()])
    get_parents.short_description = _('used by filter sets')

    def execute_function(self):
        today = datetime.date.today()
        if self.default == 'function:this_day':
            self.default = today

        if self.default == 'function:this_month':
            self.default = datetime.date(today.year, today.month, 1)

        if self.default == 'function:this_year':
            self.default = datetime.date(today.year, 1, 1)

    class Meta:
        ordering = ['name']
        verbose_name = _('filter')
        verbose_name_plural = _('filters')


class Filterset(models.Model):
    name = models.CharField(max_length=64, verbose_name=_('name'), help_text=_('A simple name for your convenience.'))
    filters = models.ManyToManyField(Filter, through='FilterExtra', verbose_name=_('filters'))

    def __unicode__(self):
        return self.name

    def get_parents(self):
        return ', '.join(['"%s"' % r.title for r in self.report_set.all()])
    get_parents.short_description = _('used by reports')

    class Meta:
        ordering = ['name']
        verbose_name = _('filters set')
        verbose_name_plural = _('filters sets')


class FilterExtra(models.Model):
    filterset = models.ForeignKey(Filterset)
    filter = models.ForeignKey(Filter, verbose_name=_('filter'))
    order = models.IntegerField(default=0, verbose_name=_('order'))

    def __unicode__(self):
        return unicode(self.filter)

    class Meta:
        verbose_name = _('filter')
        verbose_name_plural = _('filters')


class Serie(models.Model):
    data_source = models.ForeignKey(DataSource, verbose_name=_('data source'))

    name = models.CharField(max_length=64, help_text='Internal name.  Do not use spaces or special symbols.', verbose_name=_('name'))
    label = models.CharField(max_length=24, null=True, blank=True, help_text='Label to be shown to the user and to be used for the legend.', verbose_name=_('label'))
    tick_format1 = models.CharField(max_length=8, choices=SERIES_TYPE_CHOICES, verbose_name=_('tick format 1'))
    tick_format2 = models.CharField(max_length=8, choices=SERIES_TYPE_CHOICES, verbose_name=_('tick format 2'))

    query = models.TextField(verbose_name=_('query'), help_text=_('SQL query, that returns only 2 fields and may of may be a parameter query.  Include parameters in the format: <field> LIKE %(parameter)s.  Also the SQL wildcard character % must be escaped as %%.'))
    description = models.TextField(null=True, blank=True, help_text='Description of the query, notes and observations.', verbose_name=_('description'))

    validated = models.BooleanField(default=False, verbose_name=_('validated?'))
    validated_date = models.DateField(blank=True, null=True, verbose_name=_('validation date'))
    validated_person = models.CharField(max_length=32, blank=True, null=True, verbose_name=_('validated by'))
    validation_description = models.TextField(blank=True, null=True, verbose_name=_('validation description'), help_text=_('An explanation or description about how this series was validated.'))

    def __unicode__(self):
        return self.name

    def get_reports(self):
        return ', '.join(['"%s"' % report_series.report for report_series in ReportSeries.objects.filter(series=self)])
    get_reports.short_description = _('used by reports')

    def get_params(self):
        return '(%s)' % ', '.join([p for p in re.compile(r'%\((.*?)\)').findall(self.query)])
    get_params.short_description = _('parameters')

    def get_filters(self):
        filters = []
        for report in self.report_set.all():
            for set in report.filtersets.all():
                for filter in set.filters.all():
                    if filter not in filters:
                        filters.append(filter)
        return ' ,'.join(['%s' % f for f in filters])
    get_filters.short_description = _('filters')

    def execute(self, **kwargs):
        params = kwargs.get('params')
        special_params = kwargs.get('special_params')
        pipe = kwargs.get('pipe')

        if special_params:
            for sp in special_params.keys():
                query = re.compile(r'%\(' + sp + r'\)s').sub(special_params[sp], self.query)
        else:
            query = self.query

        if re.compile(r'[^%]%[^%(]').search(query):
            SeriesError(_('Single \'%\'found, replace with double \'%%\' to properly escape the SQL wildcard caracter \'%\'.'))

        cursor = self.data_source.load_backend().cursor()
        if not params:
            params = {}

        try:
            logger.debug('self.query: %s, params: %s' % (query, params))
            cursor.execute(query, params)
        except Exception as exception:
            raise SeriesError('Cursor error: %s' % exception)

        if pipe:
            pipe.send(cursor.fetchall())

        return cursor

    class Meta:
        ordering = ['name']
        verbose_name = _('serie')
        verbose_name_plural = _('series')


class Report(models.Model):
    # Base properties
    title = models.CharField(max_length=128, help_text=_('Chart title.'), verbose_name=_('title'))
    description = models.TextField(null=True, blank=True, help_text=_('A description of the report.  This description will also be presented to the user.'), verbose_name=_('description'))

    # Data
    filtersets = models.ManyToManyField(Filterset, null=True, blank=True, verbose_name=_('filter sets'))

    # Renderer properties
    renderer = models.PositiveIntegerField(choices=BACKEND_CHOICES, verbose_name=_('renderer'))
    renderer_options = models.TextField(blank=True, verbose_name=_('renderer options'))

    def __unicode__(self):
        return self.title

    def get_absolute_url(self):
        return ('ajax_report_view', [str(self.id)])
    get_absolute_url = models.permalink(get_absolute_url)

    def get_parents(self):
        return ', '.join([mi.title for mi in self.menuitem_set.all()])
    get_parents.short_description = _('used by menus')

    def get_series(self):
        return ', '.join(['"%s"' % report_series.series for report_series in self.report_series.all()])
    get_series.short_description = _('series')

    def get_backend(self):
        return import_backend(self.renderer)

    def get_parameter_values(self, request):
        params = {}
        special_params = {}

        if self.filtersets.all():
            filtersets = self.filtersets
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
                        params[filter.name] = value.strftime('%Y%m%d')
                    elif filter.type == FILTER_TYPE_COMBO:
                        special_params[filter.name] = '(' + ((''.join(['%s'] * len(value)) % tuple(value))) + ')'
                    else:
                        params[filter.name] = value

        return params, special_params

    def render(self, request):
        backend_class = self.get_backend()
        backend = backend_class()
        return backend.render(self, request)

    def execute(self, request):
        series_results = []
        deferred_list = []
        params, special_params = self.get_parameter_values(request)

        for report_series in self.report_series.all():
            # Launch all serie queries in parallel
            pipe_a, pipe_b = Pipe()
            process = Process(
                target=report_series.series.execute,
                kwargs={'pipe': pipe_a, 'params': params, 'special_params': special_params})
            process.start()
            deferred_list.append({'series': report_series.series, 'pipe': pipe_b, 'process': process})

        for deferred in deferred_list:
            # Collect the serires queries results
            deferred['process'].join()
            #series_results.append(json.dumps(deferred['pipe'].recv()))
            series_results.append(deferred['pipe'].recv())

        return series_results

    class Meta:
        ordering = ['title']
        verbose_name = _('report')
        verbose_name_plural = _('reports')


class ReportSeries(models.Model):
    report = models.ForeignKey(Report, verbose_name=_('report'), related_name='report_series')
    series = models.ForeignKey(Serie, verbose_name=_('series'))

    properties = models.TextField(blank=True, verbose_name=_('properties'))

    def __unicode__(self):
        return unicode(self.series)

    class Meta:
        verbose_name = _('report series')
        verbose_name_plural = _('reports series')


class Menuitem(models.Model):
    #TODO: reports display order
    title = models.CharField(max_length=64, verbose_name=_('title'))
    reports = models.ManyToManyField(Report, verbose_name=_('chart'), blank=True, null=True)
    order = models.IntegerField(default=0, verbose_name=_('order'))

    def __unicode__(self):
        return self.title

    class Meta:
        ordering = ['order', 'title']
        verbose_name = _('menu item')
        verbose_name_plural = _('menu items')

    def get_reports(self):
        return ', '.join(['"%s"' % r.title for r in self.reports.all()])
    get_reports.short_description = _('charts')


class UserPermission(models.Model):
    user = models.ForeignKey(User, unique=True)
    #access_unpublished_reports = models.BooleanField(default = False)
    union = models.CharField(max_length=1, choices=UNION_CHOICES, default='I', verbose_name=_('Group/user permissions union type'), help_text=_('Determines how the user permissions interact with the group permissions of this user.'))
    reports = models.ManyToManyField(Report, blank=True, null=True, verbose_name=_('charts'))
    filters = models.ManyToManyField(Filter, through='UserPermissionFilterValues', verbose_name=_('filters'))

    def get_reports(self):
        return ', '.join(['"%s"' % r.title for r in self.reports.all()])
    get_reports.short_description = _('charts')

    def __unicode__(self):
        return unicode(self.user)

    class Meta:
        verbose_name = _('user permission')
        verbose_name_plural = _('user permissions')


class UserPermissionFilterValues(models.Model):
    userpermission = models.ForeignKey(UserPermission, verbose_name=_('user permissions'))
    filter = models.ForeignKey(Filter, verbose_name=_('filter'))
    options = models.TextField(blank=True, null=True, verbose_name=_('options'))
    default = models.CharField(max_length=32, blank=True, null=True, help_text='Defautl value or one the special functions [this_day, this_month, this_year].', verbose_name=_('default'))

    def __unicode__(self):
        return '%s = %s' % (self.filter, self.options)

    class Meta:
        verbose_name = _('user filter values limit')
        verbose_name_plural = _('user filter values limits')


class GroupPermission(models.Model):
    group = models.ForeignKey(Group, unique=True, verbose_name=_('group'))
    #access_unpublished_reports = models.BooleanField(default = False)
    reports = models.ManyToManyField(Report, blank=True, null=True, verbose_name=_('reports'))
    filters = models.ManyToManyField(Filter, through='GroupPermissionFilterValues', verbose_name=_('filters'))

    def __unicode__(self):
        return unicode(self.group)

    class Meta:
        verbose_name = _('group permissions')
        verbose_name_plural = _('groups permissions')

    def get_reports(self):
        return ', '.join(['"%s"' % r.title for r in self.reports.all()])
    get_reports.short_description = _('charts')


class GroupPermissionFilterValues(models.Model):
    grouppermission = models.ForeignKey(GroupPermission, verbose_name=_('group permissions'))
    filter = models.ForeignKey(Filter, verbose_name=_('filter'))
    options = models.TextField(blank=True, null=True, verbose_name=_('options'))
    default = models.CharField(max_length=32, blank=True, null=True, help_text='Defautl value or one the special functions [this_day, this_month, this_year].', verbose_name=_('default'))

    def __unicode__(self):
        return '%s = %s' % (self.filter, self.options)

    class Meta:
        verbose_name = _('group filter values limit')
        verbose_name_plural = _('group filter values limits')
