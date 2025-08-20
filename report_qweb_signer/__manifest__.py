# Copyright 2015 Tecnativa - Antonio Espinosa
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Qweb PDF reports signer",
    "summary": "Sign Qweb PDFs usign a PKCS#12 certificate",
    "version": "18.0.1.0.0",
    "category": "Reporting",
    "website": "https://github.com/OCA/reporting-engine",
    "author": "Tecnativa, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "depends": ["certificate", "account"],
    "data": ["views/ir_actions_report_views.xml"],
    "demo": ["demo/report_partner_demo.xml", "demo/certificate_demo.xml"],
}
