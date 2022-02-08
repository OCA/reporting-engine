# Copyright 2022 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Report Dynamic",
    "version": "13.0.1.0.0",
    "category": "Report",
    "author": "Sunflower IT, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "license": "AGPL-3",
    "summary": "Dynamic Report Builder",
    "depends": ["base", "web_boolean_button"],
    "data": [
        "security/res_groups.xml",
        "security/ir_rule.xml",
        "security/ir.model.access.csv",
        "data/res_users.xml",
        "data/report_dynamic_alias.xml",
        "report/report_dynamic_report.xml",
        "views/report_dynamic.xml",
        "views/report_dynamic_section.xml",
        "views/report_dynamic_alias.xml",
        "wizards/wizard_lock_report.xml",
        "wizards/wizard_report_dynamic.xml",
    ],
    "demo": ["demo/demo.xml"],
    "installable": True,
}
