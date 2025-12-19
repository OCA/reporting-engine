# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Report Partner Address",
    "summary": "Translatable partner address details for reports and portal",
    "version": "16.0.1.0.0",
    "author": "Quartile, Odoo Community Association (OCA)",
    "category": "Reporting",
    "website": "https://github.com/OCA/reporting-engine",
    "license": "AGPL-3",
    "depends": ["web"],
    "data": [
        "views/ir_qweb_widget_templates.xml",
        "views/res_partner_views.xml",
    ],
    "maintainers": ["yostashiro", "aungkokolin1997"],
    "installable": True,
}
