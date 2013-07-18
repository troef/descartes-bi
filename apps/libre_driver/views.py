#
#    Copyright (C) 2010  Roberto Rosario
#    This file is part of descartes-bi.
#
#    descartes-bi is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    descartes-bi is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with descartes-bi.  If not, see <http://www.gnu.org/licenses/>.
#

from django.shortcuts import render
import requests

website = 'http://localhost:8000/api/sources/test/data/'


def IndexView(request):
    if request.method == 'GET':
        req = requests.get(website + '?_format=json')
        return render(request, 'libre_driver/index.html', {'json': req.json()})


def DetailView(request, json_id):
    if request.method == 'GET':
        req = requests.get(website + '{0}/?_format=json'.format(json_id))
        return render(request, 'libre_driver/detail.html', {'json': req.json()})
