# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Batch Report Printing",
    "summary": "Ability to print multiple QWeb reports in a single batch.",
    "version": "13.0.1.0.0",
    "license": "AGPL-3",
    "author": "Open Source Integrators, Odoo Community Association (OCA)",
    "category": "Reporting",
    "website": "http://www.opensourceintegrators.com",
    "depends": ["stock"],
    "data": ["security/ir.model.access.csv", "views/ir_action_report_view.xml"],
    "installable": True,
    "maintainers": ["bodedra"],
}
