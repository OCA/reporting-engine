# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
{
    "name": "Weasyprint QWEB renderer",
    "version": "12.0.1.0.0",
    "author": "Therp BV,Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Reporting",
    "summary": "Use WeasyPrint to create PDFs",
    "depends": [
        'report_qweb_custom_renderer',
        'web',
    ],
    "demo": [
        "demo/report.xml",
    ],
    "data": [
        'views/templates.xml',
    ],
    "external_dependencies": {
        'python': ['weasyprint'],
    },
}
