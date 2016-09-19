.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=====================
Report Barcode Elaphe
=====================

.. Report barcode elaphe to provide more options of barcodes and settings

This module has been built to override the method _report_barcode_ of the class _ReportController_ and provide more types and settings of barcode.
The behavior is the same as before, as you can see in the snippet below, but we have added a new query parameter(**extraopts**). html::

<img t-att-src="'/report/barcode/QR/%s' % o.name"/>


or html::

<img t-att-src="'/report/barcode?type=%s&amp;value=%s&amp;width=%s&amp;height=%s' % ('QR', o.name, 200, 200)"/>


To pass some one of those settings, you need to use the new query parameter **extraopts** and instead you write **option = value**, you need to write **option : value**. Look at this example:

``extraopts=backgroundcolor:FFFF00,barcolor:00FFFF``


E.g, img tag in HTML::

<img t-att-src="'/report/barcode?type=%s&amp;value=%s&amp;width=%s&amp;height=%s&amp;extraopts=%s' % ('CODE128', o.name, 200, 200, 'backgroundcolor:FFFF00,barcolor:00FFFF')"/>


The snippet above changes the color of the bars and the background of the barcode.
The new options of setting can be found in the [Barcode Writer in Pure PostScript documentation](https://github.com/bwipp/postscriptbarcode/wiki).

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/reporting-engine/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/reporting-engine/issues/new?body=module:%20report_barcode_elaphe%0Aversion:%209.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

* Examples taken from https://www.odoo.com/documentation/9.0/reference/reports.html.

Contributors
------------

* Jeferson Moura <jmoura@bloopark.de>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.

