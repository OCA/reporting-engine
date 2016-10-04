# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    This module copyright (C) 2014 Therp BV (<http://therp.nl>).
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
from openerp import models, fields


class IrActionsReportXml(models.Model):
    _inherit = 'ir.actions.report.xml'

    download_filename = fields.Char(
        'Download filename',
        help='Fill in this field to have a custom file name when downloading '
        'this report. This string is evaluated as a jinja2 expression.\n'
        'You can use python expressions, `objects` is a browse record list of '
        'the objects for which the report is being generated.\n'
        'Check for this list\'s length to determine if it is a report being '
        'printed for multiple records or not. You also have access to `o`, '
        'which is the first record in the list.\n'
        'For qweb reports, the variable `ext` gives you the requested format'
        '\'s extension')
