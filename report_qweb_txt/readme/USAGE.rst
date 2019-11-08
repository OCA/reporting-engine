To add a text report, you should develop an Odoo module that contains:

* a Qweb template,
* a Qweb report definition with *report_type = qweb-txt*.

This module provides a small demo report on *Users* called *CSV List*.

The module *purchase_dilicom_csv* available on the `dilicom Github repository <https://github.com/akretion/dilicom>`_ (branch *10.0*) is a better example: it adds a report *Dilicom CSV Order* on purchase orders. This report is a CSV file with one line per order line and 2 columns: EAN13 and order quantity.
