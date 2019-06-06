# Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BveViewLine(models.Model):
    _name = 'bve.view.line'
    _description = 'BI View Editor Lines'

    name = fields.Char(compute='_compute_name')
    sequence = fields.Integer(default=1)
    bve_view_id = fields.Many2one('bve.view', ondelete='cascade')
    model_id = fields.Many2one('ir.model', string='Model')
    model_name = fields.Char(compute='_compute_model_name', store=True)
    table_alias = fields.Char()
    join_model_id = fields.Many2one('ir.model', string='Join Model')
    field_id = fields.Many2one('ir.model.fields', string='Field')
    field_name = fields.Char(compute='_compute_model_field_name', store=True)
    ttype = fields.Char(string='Type')
    description = fields.Char(translate=True)
    relation = fields.Char()
    join_node = fields.Char()

    row = fields.Boolean()
    column = fields.Boolean()
    measure = fields.Boolean()
    in_list = fields.Boolean()

    @api.constrains('row', 'column', 'measure')
    def _constrains_options_check(self):
        measure_types = ['float', 'integer', 'monetary']
        for line in self:
            if line.row or line.column:
                if line.join_model_id or line.ttype in measure_types:
                    err_msg = _('This field cannot be a row or a column.')
                    raise ValidationError(err_msg)
            if line.measure:
                if line.join_model_id or line.ttype not in measure_types:
                    err_msg = _('This field cannot be a measure.')
                    raise ValidationError(err_msg)

    @api.depends('field_id', 'sequence')
    def _compute_name(self):
        for line in self:
            if line.field_id:
                field_name = line.field_id.name
                line.name = 'x_bve_%s_%s' % (line.sequence, field_name,)

    @api.depends('model_id')
    def _compute_model_name(self):
        for line in self:
            if line.model_id:
                line.model_name = line.model_id.model

    @api.depends('field_id')
    def _compute_model_field_name(self):
        for line in self:
            if line.field_id:
                field_name = line.description
                model_name = line.model_name
                line.field_name = '%s (%s)' % (field_name, model_name, )
