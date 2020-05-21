# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

{
    "name": "Report Jasper Link",
    "summary": "Link report with jasper server",
    "version": "13.0.1.0.0",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Reporting",
    "depends": ["base", "web"],
    "external_dependencies": {"python": ["suds-py3"]},
    "data": [
        "security/ir.model.access.csv",
        "views/webclient_templates.xml",
        "views/ir_actions_report_views.xml",
        "views/jasper_server_config_views.xml",
    ],
    "installable": True,
    "maintainers": ["newtratip"],
}