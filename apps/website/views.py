from django.shortcuts import render_to_response
from django.template import RequestContext

from reports.forms import FilterForm

import sys


def get_website(request, website):
    context = {}

    #Compose the URL to create LQL queries
    if website.series:
        url = website.series.data_source.load_backend().cursor().url
        query = website.series.query
        context['url'] = url + "/?" + query

    #Display the website in base_URL
    else:
        context['url'] = website.base_URL

    page = 'website/website.html'

    context['filter_form'] = FilterForm(website.filterset.all(), request.user)

    return render_to_response(page, context,
                              context_instance=RequestContext(request))


#Unused function
def get_filter_form(request, website):
    print >>sys.stderr, "Inside Get"
    url = website.series.data_source.load_backend().cursor().url
    query = website.series.query

    filter_form = FilterForm(website.filterset.all(), request.user)
    print >>sys.stderr, "got the filter_form"

    return render_to_response('website/filter_website.html',
                              {'filter_form': filter_form,
                               'url': url + "/?" + query},
                              context_instance=RequestContext(request))
