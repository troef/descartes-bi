from __future__ import absolute_import

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from reports.forms import FilterForm

from .models import Website


def website_view(request, website_pk, extra_context=None):
    website = get_object_or_404(Website, pk=website_pk)

    context = {
        'website': website
    }

    if extra_context:
        context.update(extra_context)

    if request.GET:
        form = FilterForm(website.filterset, request.user, request.GET)
        context['url'] = website.get_url(data=get_dict(form))
    else:
        form = FilterForm(website.filterset, request.user)
        context['url'] = website.get_url()

    context['form'] = form
    return render_to_response('website/website.html', context,
                              context_instance=RequestContext(request))


def get_dict(filter_form):
    """
    Use function to convert string to int.
    """
    value = {}
    for key in filter_form.data:
        if filter_form.data[key].isdigit():
            value[key] = int(filter_form.data[key])
        else:
            value[key] = filter_form.data[key]

    return value
