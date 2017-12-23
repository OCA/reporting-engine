.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

====================
Base report fill PDF
====================

This module provides a basic report class that fills pdfs.

Installation
============

Make sure you have ``fdfgen`` Python module installed::

$ pip install fdfgen

For testing it is also necessary ``pdftk`` app installed:

Ubuntu ::

    apt-get install pdftk

OSX ::

  * Install pdftk (https://www.pdflabs.com/tools/pdftk-server/).

Windows ::

  * Install pdftk (https://www.pdflabs.com/tools/pdftk-server/).

Usage
=====

An example of Fill PDF report for partners on a module called `module_name`:

A python class ::

    from odoo import models

    class PartnerFillPDF(models.AbstractModel):
        _name = 'report.module_name.report_name'
        _inherit = 'report.report_fillpdf.abstract'
    
        @api.model
        def get_original_document_path(self, data, objs):
            return get_resource_path(
                'report_fillpdf', 'static/src/pdf', 'partner_pdf.pdf')

        @api.model
        def get_document_values(self, data, objs):
            objs.ensure_one()
            return {'name': objs.name}

A computed form can be executed modifying the computing function ::

    from odoo import models

    class PartnerFillPDF(models.AbstractModel):
        _name = 'report.module_name.report_name'
        _inherit = 'report.report_fillpdf.abstract'

        @api.model
        def get_form(self, data, objs):
            return self.env['ir.attachment'].search([], limit=1)

        @api.model
        def get_document_values(self, data, objs):
            objs.ensure_one()
            return {'name': objs.name}


A report XML record ::

     <report
        id="partner_fillpdf"
        model="res.partner"
        string="Fill PDF"
        report_type="fillpdf"
        name="report_fillpdf.partner_fillpdf"
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

* Enric Tobella <etobella@creublanca.es>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
