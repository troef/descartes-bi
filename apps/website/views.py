from django.shortcuts import render_to_response
from django.template import RequestContext


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

    return render_to_response(page, context,
                              context_instance=RequestContext(request))
