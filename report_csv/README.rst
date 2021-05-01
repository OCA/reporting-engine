.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: https://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

===============
Base report csv
===============

This module provides a basic report class to generate csv report.


Usage
=====

An example of CSV report for partners on a module called `module_name`:

A python class ::

    from odoo import models

    class PartnerCSV(models.AbstractModel):
        _name = 'report.report_csv.partner_csv'
        _inherit = 'report.report_csv.abstract'

        def generate_csv_report(self, writer, data, partners):
            writer.writeheader()
            for obj in partners:
                writer.writerow({
                    'name': obj.name,
                    'email': obj.email,
                })

        def csv_report_options(self):
            res = super().csv_report_options()
            res['fieldnames'].append('name')
            res['fieldnames'].append('email')
            res['delimiter'] = ';'
            res['quoting'] = csv.QUOTE_ALL
            return res


A report XML record ::

    <report
        id="partner_csv"
        model="res.partner"
        string="Print to CSV"
        report_type="csv"
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

* Enric Tobella <etobella@creublanca.es>
* Laurent Mignon <laurent.mignon@acsone.eu>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose mission is to support the collaborative development of Odoo features and promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
