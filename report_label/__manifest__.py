# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    "name": "Report Labels",
    "version": "16.0.1.0.1",
    "summary": "Print configurable self-adhesive labels reports",
    "author": "Iván Todorovich, Moka Tourisme, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "license": "AGPL-3",
    "category": "Reporting",
    "maintainers": ["ivantodorovich"],
    "depends": [
        "base_automation",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/ir_actions_server.xml",
        "views/report_paperformat_label.xml",
        "reports/report_label.xml",
        "wizards/report_label_wizard.xml",
    ],
    "demo": [
        "demo/demo.xml",
    ],
}
