.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

=====================
Report QWeb Parameter
=====================

This module allows you to add new parameters on QWeb reports.
Currently, we have defined a field maximum on a report and a validation of
maximal and minimal size.
It is useful on xml reports in order to validate length.
XML are sometimes XSD dependant and we must validate its format.
For example, in spanish facturae (http://www.facturae.gob.es/Paginas/Index.aspx), where
length and format must be validated in several fields in order to send an invoice.


Usage
=====

#. Add a t-length attribute on report templates fields that will truncate the field
#. Add a t-minlength attribute on report template fields that will check the min length
#. Add a t-maxlength attribute on report template fields that will check the max length

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/11.0


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

* Enric Tobella <etobella@creublanca.es>


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
