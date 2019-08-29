.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

================
Base report xlsx
================

This module provides a basic report class to generate xlsx report.

Installation
============

Make sure you have ``xlsxwriter`` Python module installed::

$ pip install xlsxwriter

Usage
=====

An example of XLSX report for partners:

A python class ::

    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx

    class PartnerXlsx(ReportXlsx):
    
        def generate_xlsx_report(self, workbook, data, partners):
            for obj in partners:
                report_name = obj.name
                # One sheet by partner
                sheet = workbook.add_worksheet(report_name[:31])
                bold = workbook.add_format({'bold': True})
                sheet.write(0, 0, obj.name, bold)


    PartnerXlsx('report.res.partner.xlsx',
                'res.partner')

To manipulate the ``workbook`` and ``sheet`` objects, refer to the
`documentation <http://xlsxwriter.readthedocs.org/>`_ of ``xlsxwriter``.

A report XML record ::

    <report 
        id="partner_xlsx"
        model="res.partner"
        string="Print to XLSX"
        report_type="xlsx"
        name="res.partner.xlsx"
        file="res.partner.xlsx"
        attachment_use="False"
    />

**XLSX Header & Footer**

You can configure them on the menu *Settings > Technical > Reports > XLSX Header/Footer* following the syntax from 
`xlsxwriter documentation <https://xlsxwriter.readthedocs.io/page_setup.html#set_header>`_.

Example of Header / Footer syntax : ``&LPage &P of &N &CFilename: &F &RSheetname: &A``

On a report XML with ``report_type == 'xlsx'`` you can specified the Header and Footer you configured.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/10.0

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
* Arnaud Pineux <arnaud.pineux@acsone.eu>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
