# Copyright 2013 XCG Consulting (http://odoo.consulting)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Py3o Report Engine",
    "summary": "Reporting engine based on Libreoffice (ODT -> ODT, "
    "ODT -> PDF, ODT -> DOC, ODT -> DOCX, ODS -> ODS, etc.)",
    "version": "20.0.1.0.0",
    "category": "Reporting",
    "license": "AGPL-3",
    "author": "XCG Consulting, ACSONE SA/NV, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": ["web"],
    "external_dependencies": {
        "python": ["py3o.template", "py3o.formats", "pypdf"],
        "deb": ["libreoffice"],
    },
    "assets": {
        "web.assets_backend": [
            "report_py3o/static/src/js/py3oactionservice.esm.js",
        ],
    },
    "demo": ["demo/report_py3o.xml", "demo/py3o_pdf_options.xml"],
    "data": [
        "security/ir.access.csv",
        "views/py3o_template.xml",
        "views/ir_actions_report.xml",
        "views/py3o_pdf_options.xml",
        "views/py3o_server.xml",
    ],
    "installable": True,
}
