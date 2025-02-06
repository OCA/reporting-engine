# Copyright 2022 ForgeFlow, S.L. (http://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Partner Statement",
    "version": "17.0.1.0.1",
    "category": "Accounting & Finance",
    "summary": "OCA Financial Reports",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "maintainers": ["MiquelRForgeFlow"],
    "website": "https://github.com/OCA/account-financial-reporting",
    "license": "AGPL-3",
    "depends": ["account", "report_xlsx", "report_xlsx_helper"],
    "data": [
        "security/ir.model.access.csv",
        "security/statement_security.xml",
        "views/activity_statement.xml",
        "views/outstanding_statement.xml",
        "views/detailed_activity_statement.xml",
        "views/aging_buckets.xml",
        "views/res_config_settings.xml",
        "wizard/statement_wizard.xml",
    ],
    "assets": {
        "web.report_assets_common": [
            "/partner_statement/static/src/scss/layout_statement.scss",
        ],
    },
    "installable": True,
    "application": False,
}
