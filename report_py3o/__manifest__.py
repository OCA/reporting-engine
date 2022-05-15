# Copyright 2013 XCG Consulting (http://odoo.consulting)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Py3o Report Engine",
    "summary": "Reporting engine based on Libreoffice (ODT -> ODT, "
    "ODT -> PDF, ODT -> DOC, ODT -> DOCX, ODS -> ODS, etc.)",
    "version": "15.0.1.0.0",
    "category": "Reporting",
    "license": "AGPL-3",
    "author": "XCG Consulting," "ACSONE SA/NV," "Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": ["web"],
    "external_dependencies": {
        "python": ["py3o.template", "py3o.formats", "PyPDF2"],
        "deb": ["libreoffice"],
    },
    "assets": {
        "web.assets_backend": [
            "report_py3o/static/src/js/py3oactionservice.esm.js",
        ],
    },
    "data": [
        "security/ir.model.access.csv",
        "views/menu.xml",
        "views/py3o_template.xml",
        "views/ir_actions_report.xml",
        "demo/report_py3o.xml",
    ],
    "installable": True,
}
