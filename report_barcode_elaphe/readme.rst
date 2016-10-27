=====================
Report Barcode Elaphe
=====================

This module extends the functionality of the method _report_barcode_ of the class _ReportController_ to support more types and settings of barcode.
and to allow you to ...

Installation
============

To install this module, you need to:

* Go to `GitHub OCA/reporting-engine <https://github.com/OCA/reporting-engine>`_ and download the module.
* Move the module to your addons folder
* Go to Odoo and install the module, you can see it on the Addon's list

Usage
=====

The behavior is the same as before, you can see it with the snippet below.

    <img t-att-src="'/report/barcode/QR/%s' % o.name"/>


But we have added four new query parameters and they are:
**elaphe**, **scale**, **barmargin** and **extraopts**. You need to pass the parameter **elaphe** to indicate you want to use the new function with elaphe lib,
otherwise the old method will be used. You can see how to use them in the snippets below:

   <img t-att-src="'/report/barcode?type=%s&amp;value=%s&amp;elaphe=%s&amp;scale=%s&amp;barmargin=%s' %
   ('CODE128', o.name, 1, 4.0, 1)"/>


To pass some barcode settings, you need to use the query parameter **extraopts** and instead you write **option = value**, you need to write **option : value**. Look at this example:

   extraopts=backgroundcolor:FFFF00,barcolor:00FFFF


E.g, HTML img tag:

   <img t-att-src="'/report/barcode?type=%s&amp;value=%s&amp;elaphe=%s&amp;scale=%s&amp;extraopts=%s' %
   ('code128', o.name, 1, 4.0, 'backgroundcolor:FFFF00,barcolor:00FFFF')"/>


The snippet above changes the color of the bars and the background of the barcode.
The new options of setting can be found in the `Barcode Writer in Pure PostScript documentation <https://github.com/bwipp/postscriptbarcode/wiki>`_.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/reporting-engine/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* bloopark system
* Jeferson Moura <jmoura@bloopark.de>

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