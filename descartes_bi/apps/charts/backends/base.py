from django.utils.translation import ugettext_lazy as _


class ChartBackend(object):
    _registry = {}
    label = _('Chart base class')
