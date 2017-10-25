.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

================
Base report xlsx
================

This module provides a basic report class to generate xlsx report.

Installation
============

Make sure you have ``xlsxwriter`` Python module installed::

$ pip install xlsxwriter

For testing it is also necessary ``xlrd`` Python module installed::

$ pip install xlrd

Usage
=====

An example of XLSX report for partners on a module called `module_name`:

A python class ::

    from odoo import models

    class PartnerXlsx(models.AbstractModel):
        _name = 'report.module_name.report_name'
        _inherit = 'report.report_xlsx.abstract'
    
        def generate_xlsx_report(self, workbook, data, partners):
            for obj in partners:
                report_name = obj.name
                # One sheet by partner
                sheet = workbook.add_worksheet(report_name[:31])
                bold = workbook.add_format({'bold': True})
                sheet.write(0, 0, obj.name, bold)

To manipulate the ``workbook`` and ``sheet`` objects, refer to the
`documentation <http://xlsxwriter.readthedocs.org/>`_ of ``xlsxwriter``.

A report XML record ::

    <report 
        id="partner_xlsx"
        model="res.partner"
        string="Print to XLSX"
        report_type="xlsx"
        name="module_name.report_name"
        file="res_partner"
        attachment_use="False"
    />

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

Contributors
------------

* Adrien Peiffer <adrien.peiffer@acsone.eu>
* Enric Tobella <etobella@creublanca.es>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
