# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Report Positioned Image",
    "summary": "Add positioned images to PDF reports.",
    "version": "18.0.1.0.0",
    "category": "Reporting",
    "author": "Quartile, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "license": "AGPL-3",
    "depends": ["web", "report_qweb_element_page_visibility"],
    "data": [
        "security/ir.model.access.csv",
        "security/report_positioned_image_security.xml",
        "views/report_positioned_image_views.xml",
        "views/res_company_views.xml",
        "views/ir_actions_report_views.xml",
    ],
    "installable": True,
}
