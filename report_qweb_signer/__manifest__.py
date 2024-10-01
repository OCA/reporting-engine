# Copyright 2015 Tecnativa - Antonio Espinosa
# Copyright 2017 Tecnativa - Pedro M. Baeza
# Copyright 2018 Tecnativa - David Vidal
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Qweb PDF reports signer",
    "summary": "Sign Qweb PDFs usign a PKCS#12 certificate",
    "version": "16.0.1.0.2",
    "category": "Reporting",
    "website": "https://github.com/OCA/reporting-engine",
    "author": "Tecnativa, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["web_editor"],
    "external_dependencies": {
        "python": ["endesive", "cryptography"],
        "deb": ["default-jre-headless"],
    },
    "data": [
        "data/defaults.xml",
        "security/ir.model.access.csv",
        "views/report_certificate_view.xml",
        "views/res_company_view.xml",
    ],
    "demo": ["demo/report_partner_demo.xml", "demo/report_certificate_demo.xml"],
}
