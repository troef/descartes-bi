from django.utils.translation import ugettext_lazy as _


class ChartBackend(object):
    """
    Base class for the chart rendering backend.
    """
    label = _('Chart base class')

    def render(self, report, request):
        """Each backend must override this method. Method must return an
        HttpResponse or subclass, which is passed directly to the calling
        view.
        """
        raise NotImplemented
