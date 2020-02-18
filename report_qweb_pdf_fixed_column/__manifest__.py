# Copyright 2020 Tecnativa - Alexandre Díaz
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Report Qweb PDF Fixed Column',
    'summary': """
        Fix auto-col to not change report font size caused by a
        boundary overflow""",
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'category': 'Reporting',
    'author': 'Tecnativa, Odoo Community Association (OCA)',
    'website': 'https://github.com/OCA/reporting-engine',
    'depends': [
        'web',
    ],
    'data': [
        'views/assets.xml',
    ],
    'maintainers': ['Tardo'],
    'development_status': 'Beta',
}
