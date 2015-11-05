# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2010-2013 OpenERP s.a. (<http://openerp.com>).
#    Copyright (C) 2013 initOS GmbH(<http://www.initos.com>).
#    Author Nikolina Todorova <nikolina.todorova@initos.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Pdf form fill',
    'version': '0.1.0',
    'author': 'initOS GmbH',
    'category': '',
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
    'images': [],
    'depends': [
    ],
    'external_dependencies': {
        'python': ['fdfgen'],
    },
    'data': [
    ],
    'js': [
    ],
    'qweb': [
    ],
    'css': [
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
}
