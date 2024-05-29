# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
{
    "name": "Report Async",
    "summary": "Central place to run reports live or async",
    "version": "16.0.1.0.1",
    "author": "Ecosoft, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Generic Modules",
    "depends": ["queue_job", "spreadsheet_dashboard"],
    "data": [
        "security/ir.model.access.csv",
        "security/ir_rule.xml",
        "data/mail_template.xml",
        "data/queue_job_function_data.xml",
        "views/report_async.xml",
        "wizard/print_report_wizard.xml",
    ],
    "demo": ["demo/report_async_demo.xml"],
    "installable": True,
    "maintainers": ["kittiu"],
    "development_status": "Beta",
}
