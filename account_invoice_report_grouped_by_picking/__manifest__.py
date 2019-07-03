# Copyright 2017-2019 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Account Invoice Grouped by Picking",
    "summary": "Print invoice lines grouped by picking",
    "version": "11.0.1.4.0",
    "category": "Accounting & Finance",
    "website": "https://github.com/OCA/account-invoice-reporting",
    "author": "Tecnativa, "
              "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": [
        "stock_picking_invoice_link",
    ],
    "data": [
        "security/portal_security.xml",
        "views/report_invoice.xml",
    ],
}
