# © 2016 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    "name": "Pdf watermark",
    "version": "17.0.1.0.0",
    "author": "Therp BV, " "Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "category": "Technical Settings",
    "development_status": "Production/Stable",
    "summary": "Add watermarks to your QWEB PDF reports",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": ["web"],
    "data": [
        "demo/report.xml",
        "views/ir_actions_report_xml.xml",
        "views/res_company.xml",
    ],
    "assets": {
        "web.report_assets_pdf": [
            "/report_qweb_pdf_watermark/static/src/css/report_qweb_pdf_watermark.css"
        ],
    },
    "demo": ["demo/report.xml"],
    "installable": True,
}
