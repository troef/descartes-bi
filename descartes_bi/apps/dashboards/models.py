from django.db import models
from django.utils.translation import ugettext_lazy as _

from reports.models import Report, Filterset
from website.models import Website

ELEMENT_CHART = 1
ELEMENT_WEBSITE = 2

ELEMENT_CHOICES = (
    (ELEMENT_CHART, _('chart')),
    (ELEMENT_WEBSITE, _('website'))
)


class Dashboard(models.Model):
    label = models.CharField(max_length=64, verbose_name=_(u'label'))

    def __unicode__(self):
        return self.label

    def active_elements(self):
        return self.elements.filter(enabled=True)

    class Meta:
        verbose_name = _('dashboard')
        verbose_name_plural = _('dashboards')


class DashboardElement(models.Model):
    dashboard = models.ForeignKey(Dashboard, verbose_name=_(u'dashboard'), related_name='elements')
    enabled = models.BooleanField(default=True, verbose_name=_('enabled'))
    span = models.PositiveIntegerField(verbose_name=_(u'span'), help_text=_('The amount of columns in a 12 columns layout that this element should occupy.'))
    visual_type = models.PositiveIntegerField(choices=ELEMENT_CHOICES)
    report = models.ForeignKey(Report, verbose_name=_(u'report'), blank=True, null=True)
    website = models.ForeignKey(Website, verbose_name=_(u'website'), blank=True, null=True)
    filtersets = models.ForeignKey(Filterset, null=True, blank=True)
    values = models.TextField(blank=True)

    @property
    def label(self):
        if self.report:
            return unicode(self.report)
        else:
            return unicode(self.website)

    @property
    def load_url(self):
        if self.report:
            return self.report.get_absolute_url()
        elif self.website:
            return self.website.get_url()

    def __unicode__(self):
        return self.label

    class Meta:
        verbose_name = _('dashboard element')

# Legacy dashboard element processing
"""
    links = {}
    for widget in dashboard.widgets.all():
        if widget.report:
            get_form = ""
            if widget.filtersets:
                filterform = widget.filtersets.filters.all()
                values = widget.values.split(',')
                for index in range(len(values)):
                    get_form += filterform[index].name + "=" + values[index] + "&"

            lk = reverse('reports:ajax_report_view', args=[widget.report.id])# + "/?" + get_form + "output_type=" + sp.visual_type
            links[str(widget.id)] = lk
        if widget.website:
            query = widget.website.series.query
            if widget.website.filterset.exists():
                filterform = widget.filtersets.filters.all()
                values = widget.values.split(',')
                dic = {}
                for index in range(len(values)):
                    if values[index].isdigit():
                        dic[filterform[index].name] = int(values[index])
                    else:
                        dic[filterform[index].name] = values[index]
                query = query % dic
            if widget.website.base_URL:
                links["mapdiv" + str(widget.id)] = widget.website.base_URL + "/?" + query
            else:
                links["mapdiv" + str(widget.id)] = widget.website.series.data_source.load_backend().cursor().url + "/?" + query
    context = {'dashboard': dashboard, 'links': links}
    page = 'dashboards/dashboard.html'
"""
