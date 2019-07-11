# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Report Substitute',
    'summary': """
        This addon give the possibility to substitute a report action by 
        another based on some criteria.
        """,
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV,'
              'Odoo Community Association (OCA)',
    'website': 'https://github.com/acsone/reporting-engine',
    'depends': ['base'],
    'data': [
        'security/ir_actions_report_substitution_criteria.xml',
        'views/ir_actions_report.xml',
    ],
}
