# © 2019  Vauxoo (<http://www.vauxoo.com/>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    'name': 'Reporting Engine Configuration',
    'version': '12.0.1.0.0',
    'author': 'TenovarLTD',
    'website': 'https://www.tenovar.com',
    'description' : """This repository hosts alternative reporting 
                    engines to the ones included on Odoo core (RML, QWeb and Webkit). 
                    It is complemented with the ones that host the reports theirself:

                    https://github.com/OCA/account-financial-reporting 
                    https://github.com/OCA/purchase-reporting https://github.com/OCA/sale-reporting ...

                    The convention is to use a suffix to each module to indicate 
                    that its for using with that report engine (for example, account_invoice_report_birt 
                    or sale_order_report_pentaho).

                    It can contain also another utilities directly involved 
                    with reports (like merge/split utils, checkers, signing tools and so on).""" ,

    'license': 'AGPL-3',
    'category': 'Tools',
    'depends': [
        'base_setup',
    ],
    'data': [        
        'views/res_config_settings_views.xml',       
    ],
    'installable': True,
    'auto_install': False,
    
}
