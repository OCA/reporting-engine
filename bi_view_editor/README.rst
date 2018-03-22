.. image:: https://img.shields.io/badge/license-AGPL--3-blue.png
   :target: https://www.gnu.org/licenses/agpl
   :alt: License: AGPL-3

==============
BI View Editor
==============

BI View Editor is a tool integrated in Odoo that allows users define and
execute their own reports without the need to code.

Purpose:

* The BI View Editor is used to create reports not already contained in the
  standard Odoo, combining data from existing sources.

* It has been designed to be used by users with little or no knowledge of
  the technical architecture of Odoo. Users visually link business objects
  and select the fields to visualize.

* The BI View Editor offers users different types of representations,
  including tree, graph, pivot views.


Usage
=====


To graphically design your analysis data-set:

- From the Dashboards menu, select "Custom BI Views"
- Browse trough the business objects in the Query tab
- Pick the interesting fields (Drag & Drop)
- For each selected field, right-click on the Options column and select whether it's a row, column or measure; if you want to remove the field from the list view, unflag the checkbox ´List´ in the Options column
- Save and click "Generate BI View"
- Click "Open BI View" to view the result
- If module Dashboard (board) is installed, the standard "Add to My Dashboard" functionality would be available
- Click "Create a menu" to create a new menu item directly linked to your new BI view (this feature is available in developer mode); when the BI view is reset back to draft this menu will be removed, and you will need to re-create the menu entry.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/11.0

Known issues / Roadmap
======================

* Non-stored fields and many2many fields are not supported
* Provide graph view for table relations
* Extend the capabilities of the tree views (e.g. add sums)
* Provide a tutorial (eg. a working example of usage)
* Implement a more advanced UI, with possibilities to use LEFT JOIN as default instead of INNER JOIN
* Find better ways to extend the *_auto_init()* without override (possibly avoid the monkey patch)
* Data the user has no access to (e.g. in a multi company situation) can be viewed by making a view
* Store the JSON data structure in ORM
* Would be nice if models available to select when creating a view are limited to the ones that have intersecting groups (for non technical users)

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/reporting-engine/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Simon Janssens <s.janssens@onestein.nl>
* Diego Luis Neto <diegoluis.neto@gmail.com>
* Dennis Sluijk <d.sluijk@onestein.nl>
* Kevin Graveman <k.graveman@onestein.nl>
* Richard Dijkstra <r.dijkstra@onestein.nl>
* Andrea Stirpe <a.stirpe@onestein.nl>
* Antonio Esposito <a.esposito@onestein.nl>
* Jordi Ballester Alomar <jordi.ballester@eficent.com>

Do not contact contributors directly about support or help with technical issues.

Funders
-------

The development of this module has been financially supported by:

* IDEAL Connaissances SAS https://www.idealconnaissances.com

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
