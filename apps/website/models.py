from django.db import models
from django.utils.translation import ugettext_lazy as _


class Website(models.Model):
    label = models.CharField(max_length=32)
    base_URL = models.CharField(max_length=256, blank=True)
    # data_source = models.ForeignKey(DataSource, verbose_name=_(u'data_source'), blank=True)
    series = models.ForeignKey('reports.Serie', verbose_name=_(u"series"), blank=True)
    filterset = models.ForeignKey('reports.Filterset', verbose_name=_(u'filterset'), blank=True)

    def __unicode__(self):
        return self.label
