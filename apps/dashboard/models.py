from django.db import models
from django import forms
from reports.models import Report , Filter

# Create your models here.

class selected_report(models.Model):
	rep_id = models.ForeignKey(Report)
	from_date = models.DateField('From Date')
	to_date = models.DateField('To Date')
	id_regional = models.PositiveSmallIntegerField('Regional ID')
	visual_type = models.CharField(max_length=5, choices=(('chart', 'chart') , ('grid', 'grid')), default='chart')
	refresh_rate = models.PositiveSmallIntegerField('Refresh Rate')

	def __unicode__(self):
		return self.rep_id.title + "{" + str(self.from_date) + "}" 

class dash(models.Model):
	name = models.CharField(max_length=50)
	selection_list = models.ManyToManyField(selected_report)

	def __unicode__(self):
		return self.name







