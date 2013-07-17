from django.shortcuts import render , get_object_or_404

from reports.models import Report

from dashboard.models import dash

def index(request):
	report_list = Report.objects.all()
	context = {'report_list': report_list }
	return render(request, 'dashboard/test.html', context)

def display(request, dash_id):
	dash_board = get_object_or_404(dash, pk=dash_id)
	selected_reports = dash_board.selection_list.all()
	context =  {'selected_reports' : selected_reports }
	return render(request, 'dashboard/dash_list.html', context)