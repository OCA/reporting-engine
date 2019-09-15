###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Autovacuum 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import time
import base64
import logging
import datetime
import dateutil

from pytz import timezone

from odoo import _
from odoo import models, api, fields
from odoo.exceptions import ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.safe_eval import safe_eval, test_python_expr

_logger = logging.getLogger(__name__)

class AutoVacuumRules(models.Model):
    
    _name = 'muk_autovacuum.rules'
    _description = "Auto Vacuum Rules"
    _order = "sequence asc"
    
    #----------------------------------------------------------
    # Defaults
    #----------------------------------------------------------

    def _default_sequence(self):
        record = self.sudo().search([], order='sequence desc', limit=1)
        if record.exists():
            return record.sequence + 1
        else:
            return 1

    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    name = fields.Char(
        string='Name',
        required=True)
    
    active = fields.Boolean(
        string='Active',
        default=True)
    
    state = fields.Selection(
        selection=[
            ('time', 'Time Based'),
            ('size', 'Size Based'),
            ('domain', 'Domain Based'),
            ('code', 'Code Based')],
        string='Rule Type', 
        default='time',
        required=True)

    sequence = fields.Integer(
        string='Sequence',
        default=lambda self: self._default_sequence(),
        required=True)
    
    model = fields.Many2one(
        comodel_name='ir.model',
        string="Model",
        required=True,
        ondelete='cascade',
        help="Model on which the rule is applied.")
    
    model_name = fields.Char(
        related='model.model',
        string="Model Name",
        readonly=True,
        store=True)
    
    time_field = fields.Many2one(
        comodel_name='ir.model.fields',
        domain="[('model_id', '=', model), ('ttype', '=', 'datetime')]", 
        string='Time Field',
        ondelete='cascade',
        states={
            'time': [('required', True)], 
            'size': [('invisible', True)], 
            'domain': [('invisible', True)], 
            'code': [('invisible', True)]})
    
    time_type = fields.Selection(
        selection=[
            ('minutes', 'Minutes'),
            ('hours', 'Hours'),
            ('days', 'Days'),
            ('weeks', 'Weeks'),
            ('months', 'Months'),
            ('years', 'Years')],
        string='Time Unit', 
        default='months',
        states={
            'time': [('required', True)], 
            'size': [('invisible', True)], 
            'domain': [('invisible', True)], 
            'code': [('invisible', True)]})
    
    time = fields.Integer(
        string='Time', 
        default=1, 
        states={
            'time': [('required', True)], 
            'size': [('invisible', True)], 
            'domain': [('invisible', True)], 
            'code': [('invisible', True)]},
        help="Delete older data than x.")
    
    size_type = fields.Selection(
        selection=[
            ('fixed', 'Fixed Value'),
            ('parameter', 'System Parameter')],
        string='Size Type', 
        default='fixed',
        states={
            'time': [('invisible', True)], 
            'size': [('required', True)], 
            'domain': [('invisible', True)], 
            'code': [('invisible', True)]})
    
    size_parameter = fields.Many2one(
        comodel_name='ir.config_parameter', 
        string='System Parameter',
        ondelete='cascade',
        states={
            'time': [('invisible', True)], 
            'size': [('required', True)], 
            'domain': [('invisible', True)], 
            'code': [('invisible', True)]})
    
    size_parameter_value = fields.Integer(
        compute='_compute_size_parameter_value',
        string='Size Value', 
        states={
            'time': [('invisible', True)], 
            'size': [('readonly', True)], 
            'domain': [('invisible', True)], 
            'code': [('invisible', True)]},
        help="Delete records with am index greater than x.")
    
    size_order = fields.Char(
        string='Size Order',
        default='create_date desc',
        states={
            'time': [('invisible', True)], 
            'size': [('required', True)], 
            'domain': [('invisible', True)], 
            'code': [('invisible', True)]},
        help="Order by which the index is defined.")
    
    size = fields.Integer(
        string='Size', 
        default=200, 
        states={
            'time': [('invisible', True)], 
            'size': [('required', True)], 
            'domain': [('invisible', True)], 
            'code': [('invisible', True)]},
        help="Delete records with am index greater than x.")
    
    domain = fields.Char(
        string='Domain',
        states={
            'time': [('invisible', True)], 
            'size': [('invisible', True)], 
            'domain': [('required', True)], 
            'code': [('invisible', True)]},
        help="Delete all records which match the domain.")
    
    code = fields.Text(
        string='Code',
        states={
            'time': [('invisible', True)], 
            'size': [('invisible', True)], 
            'domain': [('invisible', True)] ,
            'code': [('required', True)]},
        default="# Enter Python code here. Help about Python expression is available in the help tab of this document.",
        help="Code which will be executed during the clean up.")
    
    protect_starred = fields.Boolean(
        string='Protect Starred', 
        default=True,  
        states={
            'time': [('invisible', False)], 
            'size': [('invisible', True)], 
            'domain': [('invisible', True)], 
            'code': [('invisible', True)]},
        help="""Do not delete starred records.
            Checks for the following fields:
                - starred
                - favorite
                - is_starred
                - is_favorite""")
    
    only_inactive = fields.Boolean(
        string='Only Archived', 
        default=False,  
        states={
            'time': [('invisible', False)],
            'size': [('invisible', True)],
            'domain': [('invisible', True)], 
            'code': [('invisible', True)]},
        help="Only delete archived records.")
    
    only_attachments = fields.Boolean(
        string='Only Attachments', 
        default=False,
        states={
            'time': [('invisible', False)],
            'size': [('invisible', False)],
            'domain': [('invisible', False)], 
            'code': [('invisible', True)]},
        help="Only delete record attachments.")
    
    #----------------------------------------------------------
    # Functions
    #----------------------------------------------------------
    
    @api.model
    def _get_eval_domain_context(self):
        return {
            'datetime': datetime,
            'dateutil': dateutil,
            'timezone': timezone,
            'time': time,
            'uid': self.env.uid,
            'user': self.env.user
        }
    
    @api.model
    def _get_eval_code_context(self, rule):
        return {
            'env': self.env,
            'model': self.env[rule.model_name],
            'uid': self.env.user.id,
            'user': self.env.user,
            'time': time,
            'datetime': datetime,
            'dateutil': dateutil,
            'timezone': timezone,
            'b64encode': base64.b64encode,
            'b64decode': base64.b64decode,
            'date_format': DEFAULT_SERVER_DATE_FORMAT,
            'datetime_format': DEFAULT_SERVER_DATETIME_FORMAT,
            'Warning': Warning,
            'logger': logging.getLogger("%s (%s)" % (__name__, rule.name)),
        }
    
    #----------------------------------------------------------
    # View
    #----------------------------------------------------------
    
    @api.onchange('model')
    def _onchange_model(self):
        field_domain = [
            ('model_id', '=', self.model.id),
            ('ttype', '=', 'datetime'),
            ('name', '=', 'create_date')]
        model = self.env['ir.model.fields'].sudo()
        self.time_field = model.search(field_domain, limit=1)

    @api.model
    def get_import_templates(self):
        return [{
            'label': _('Import Template for Auto Vacuum Rules'),
            'template': '/muk_autovacuum/static/xls/muk_autovacuum_rules.xls'
        }]

    #----------------------------------------------------------
    # Read
    #----------------------------------------------------------
    
    @api.depends('size_parameter')
    def _compute_size_parameter_value(self):
        for record in self:
            try:
                record.size_parameter_value = int(record.size_parameter.value)
            except ValueError:
                record.size_parameter_value = None
                
    #----------------------------------------------------------
    # Create, Update, Delete
    #----------------------------------------------------------
    
    @api.constrains('code')
    def _check_code(self):
        for record in self.sudo().filtered('code'):
            message = test_python_expr(expr=record.code.strip(), mode="exec")
            if message:
                raise ValidationError(message)
    
    @api.constrains(
        'state', 'model', 'domain', 'code',
        'time_field', 'time_type', 'time',
        'size_type', 'size_parameter', 'size_order', 'size')
    def _validate(self):
        validators = {
            'time': lambda rec: rec.time_field and rec.time_type and rec.time,
            'size': lambda rec: rec.size_order and (rec.size_parameter or rec.size),
            'domain': lambda rec: rec.domain,
            'code': lambda rec: rec.code,
        }
        for record in self:
            if not validators[record.state](record):
                raise ValidationError(_("Rule validation has failed!"))