# Copyright 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Py3o Report Engine - Fusion server support",
    "summary": "Let the fusion server handle format conversion.",
    "version": "14.0.1.0.0",
    "category": "Reporting",
    "license": "AGPL-3",
    "author": "XCG Consulting,"
    "ACSONE SA/NV,"
    "Akretion,"
    "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": ["report_py3o"],
    "external_dependencies": {
        "python": ["py3o.template", "py3o.formats"],
        "deb": ["libreoffice"],
    },
    "demo": ["demo/report_py3o.xml", "demo/py3o_pdf_options.xml"],
    "data": [
        "views/ir_actions_report.xml",
        "security/ir.model.access.csv",
        "views/py3o_server.xml",
        "views/py3o_pdf_options.xml",
    ],
    "installable": True,
}
