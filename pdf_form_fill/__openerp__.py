# -*- coding: utf-8 -*-
# © initOS GmbH 2013
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
{
    'name': 'Pdf form fill',
    'version': '7.0.1.0.0',
    'author': 'initOS GmbH, Odoo Community Association (OCA)',
    'description': """
The user should be able to fill .pdf form by mapping the fields from a record.
The user should be able to download the filled .pdf form.

Pdf fillable form means that you can fill out the information required by
typing directly in the pdf.
That is done by creating fillable fields in the pdf document.
The idea of this module is to map openerp model fields to those fillable pdf
fields which will make possible the automatic filling the forms for all model
records. To do that you will need the .pdf fillable field names and the
corresponding model field names.
After we have the filed pdf we can use the implemented functionality
to download it.
""",
    'website': 'http://www.initos.com',
    'license': 'AGPL-3',
    'data': [
        "security/ir.model.access.csv",
    ],
    'external_dependencies': {
        'python': ['fdfgen'],
    },
    'installable': True,
    'auto_install': False,
}
