.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===========================
Base report pdf-combination
===========================

This module provides a basic report class to generate pdf from other pdf files.

Installation
============

Make sure you have ``PyPDF2`` Python module installed::

$ pip install PyPDF2

Usage
=====

An example of pdf-combination report for partners on a module called `module_name`:

A python class ::

    from odoo import models

    class PartnerPdfCombination(models.AbstractModel):
        _name = 'report.module_name.report_name'
        _inherit = 'report.report_pdf_combination.abstract'
    
        def get_files_for_pdf_combination_report(self, data, partners):
            file_list = []
            for obj in partners:
                # [...]
                file_list.append(file_like_object)
            return file_list

A report XML record ::

    <report 
        id="partner_pdf_combination"
        model="res.partner"
        string="Print Big Report"
        report_type="pdf-combination"
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

`report_xlsx <https://github.com/OCA/reporting-engine/tree/11.0/report_xlsx>`__ was used as template for this module.

Contributors
------------

* `Ivan Yelizariev <https://it-projects.info/team/yelizariev>`__

Funders
-------

The development of this module has been financially supported by:

* `e-thos SSII <http://www.e-thos.fr>`__

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
