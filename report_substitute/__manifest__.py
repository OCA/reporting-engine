# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Report Substitute',
    'summary': """
        This module allows to create substitution rules for report actions.
        """,
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/reporting-engine',
    'depends': ['base', 'mail'],
    'data': [
        'security/ir_actions_report_substitution_rule.xml',
        'views/assets_backend.xml',
        'views/ir_actions_report.xml',
    ],
    'demo': ['demo/action_report.xml'],
}
