Descartes-bi
=============

Descartes-bi is a database agnostic, Django based business intelligence tool.

![screenshot](https://raw.github.com/rosarior/descartes-bi/master/docs/_static/screenshot.png)

Implementation
--------------

Descartes-bi encapsulates small snipets of SQL in pseudo-objects called series, that can later be combined to create comparative charts.  Aside from containing series, charts can also define parameters for user interaction.  Parameters (called filters) can be programmed to be restrictive using a custom permission system.


Requirements
------------

 * Django 1.5.1


Setting up
----------

By default the project is set up to run on a SQLite database. Run::

    $ python manage.py syncdb --migrate


Executing
---------

Use:

    $ python manage.py runserver



Creating charts
---------------

Go into the admin site and start creating SQL queries to extract data from your data source DB and combine them into different charts.

To do
-----

* Written documentation
* Remove Superfish as convert menu to play HTML+CSS menu
* Printer output support - Print CSS file
* Add intellingent js thousand comma
* Report timeout -> to avoid infinite "LOADING..."
* Please "LOGIN" callout in open panel for clueless users :S
* Angled label text
* Stacked bars
* Per user Favorites charts
* New chart type - endless timeline
* New chart type - 3d bar
* Allow anonymous access to reports
* Date helpers (This month, prev. month, this year, prev year, fiscal year, prev fiscal year)
* Chart sets w/ same parameters  ie: monthly report
* Drilldowns


License
-------
Descartes-bi is licensed under the terms of the GNU License version 3, see the included LICENSE file.
