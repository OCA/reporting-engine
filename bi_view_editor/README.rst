.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
BI View Editor
==============

The module BI View Editor is user-friendly tool (Query Builder) integrated in Odoo.
It creates views for Odoo 8, allowing the user to specify graphically the sources
and the attributes of the data-set to analyze, automating all the operations for
creating all the necessary low level Odoo objects.


It is intended for:

- Graphically define your analysis data-set
- Add new computed information to your data set
- Specify the visualization attributes
- Create the basis for a new data exploration method in Odoo


Benefits would be:

- More freedom to consultants or end users to customize views
- No more external tools for data analysis
- Easy update of your BI reports
- No more external tools for data analysis



Usage
=====


To graphically design your analysis data-set:

- From the Reporting menu, select "Custom BI Views"
- Browse trough the business objects in the Query tab
- Pick the interesting fields (Drag & Drop)
- Save and click "Generate BI View"



.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/8.0

Known issues / Roadmap
======================

* Non-stored fields are not supported yet
* Provide graph view for table relations (would be a "nice to have")
* Porting to Odoo 9.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/reporting-engine/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
reporting-engine/issues/new?body=module:%20
bi_view_editor%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

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
