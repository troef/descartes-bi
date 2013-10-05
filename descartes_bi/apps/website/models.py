from django.db import models
from django.utils.translation import ugettext_lazy as _

from reports.forms import FilterForm
from reports.models import Serie, Filterset


class Website(models.Model):
    label = models.CharField(max_length=32)
    base_URL = models.CharField(max_length=256, blank=True)
    series = models.ForeignKey(Serie, verbose_name=_(u'series'), blank=True, null=True)
    filterset = models.ManyToManyField(Filterset, verbose_name=_(u'filterset'), blank=True, null=True)

    # TODO: Add authehtication
    # TODO: username & password

    def get_url(self, data=None):
        if self.series:
            if data:
                return self.series.data_source.load_backend().cursor().url + '/?' + self.series.query % data
            else:
                if self.filterset.exists():
                    return None
                else:
                    return self.series.data_source.load_backend().cursor().url + '/?' + self.series.query
        else:
            # Display the website in base_URL
            return self.base_URL

    def __unicode__(self):
        return self.label



