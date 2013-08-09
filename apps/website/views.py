from django.shortcuts import render_to_response
from django.template import RequestContext

from reports.forms import FilterForm


def get_website(request, website):
    context = {}
    #Compose the URL to create LQL queries
    if website.series:
        url = website.series.data_source.load_backend().cursor().url
        query = website.series.query

        if request.method == 'GET' and website.filterset.exists():
            filtersets = website.filterset

            if request.GET:
                filter_form = FilterForm(filtersets, request.user, request.GET)
                value = get_value(request, filter_form, filtersets)
                query = query % value
                context['url'] = url + "/?" + query
            else:
                filter_form = FilterForm(filtersets, request.user)

            context['filter_form'] = filter_form
        else:
            context['url'] = url + "/?" + query

    #Display the website in base_URL
    else:
        context['url'] = website.base_URL

    page = 'website/website.html'

    return render_to_response(page, context,
                              context_instance=RequestContext(request))


def get_value(request, filter_form, filtersets):
    for set in filtersets.all():
        for filter in set.filters.all():

            if filter_form.is_valid():
                value = filter_form.cleaned_data[filter.name]
                return {filter.name: value}
