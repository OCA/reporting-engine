# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import re

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class BiSQLViewField(models.Model):
    _name = 'bi.sql.view.field'
    _description = 'Bi SQL View Field'
    _order = 'sequence'

    _TTYPE_SELECTION = [
        ('boolean', 'boolean'),
        ('char', 'char'),
        ('date', 'date'),
        ('datetime', 'datetime'),
        ('float', 'float'),
        ('integer', 'integer'),
        ('many2one', 'many2one'),
        ('selection', 'selection'),
    ]

    _GRAPH_TYPE_SELECTION = [
        ('col', 'Column'),
        ('row', 'Row'),
        ('measure', 'Measure'),
    ]

    _TREE_VISIBILITY_SELECTION = [
        ('unavailable', 'Unavailable'),
        ('hidden', 'Hidden'),
        ('available', 'Available'),
    ]

    # Mapping to guess Odoo field type, from SQL column type
    _SQL_MAPPING = {
        'boolean': 'boolean',
        'bigint': 'integer',
        'integer': 'integer',
        'double precision': 'float',
        'numeric': 'float',
        'text': 'char',
        'character varying': 'char',
        'date': 'datetime',
        'timestamp without time zone': 'datetime',
    }

    name = fields.Char(string='Name', required=True, readonly=True)

    sql_type = fields.Char(
        string='SQL Type', required=True, readonly=True,
        help="SQL Type in the database")

    sequence = fields.Integer(string='sequence', required=True, readonly=True)

    bi_sql_view_id = fields.Many2one(
        string='SQL View', comodel_name='bi.sql.view', ondelete='cascade')

    is_index = fields.Boolean(
        string='Is Index', help="Check this box if you want to create"
        " an index on that field. This is recommended for searchable and"
        " groupable fields, to reduce duration")

    is_group_by = fields.Boolean(
        string='Is Group by', help="Check this box if you want to create"
        " a 'group by' option in the search view")

    index_name = fields.Char(
        string='Index Name', compute='_compute_index_name')

    graph_type = fields.Selection(
        string='Graph Type', selection=_GRAPH_TYPE_SELECTION)

    tree_visibility = fields.Selection(
        string='Tree Visibility', selection=_TREE_VISIBILITY_SELECTION,
        default='available', required=True)

    field_description = fields.Char(
        string='Field Description', help="This will be used as the name"
        " of the Odoo field, displayed for users")

    ttype = fields.Selection(
        string='Field Type', selection=_TTYPE_SELECTION, help="Type of the"
        " Odoo field that will be created. Keep empty if you don't want to"
        " create a new field. If empty, this field will not be displayed"
        " neither available for search or group by function")

    selection = fields.Text(
        string='Selection Options', default='[]',
        help="For 'Selection' Odoo field.\n"
        " List of options, specified as a Python expression defining a list of"
        " (key, label) pairs. For example:"
        " [('blue','Blue'), ('yellow','Yellow')]")

    many2one_model_id = fields.Many2one(
        comodel_name='ir.model', string='Model',
        help="For 'Many2one' Odoo field.\n"
        " Comodel of the field.")

    # Constrains Section
    @api.constrains('is_index')
    @api.multi
    def _check_index_materialized(self):
        for rec in self.filtered(lambda x: x.is_index):
            if not rec.bi_sql_view_id.is_materialized:
                raise UserError(_(
                    'You can not create indexes on non materialized views'))

    # Compute Section
    @api.multi
    def _compute_index_name(self):
        for sql_field in self:
            sql_field.index_name = '%s_%s' % (
                sql_field.bi_sql_view_id.view_name, sql_field.name)

    # Overload Section
    @api.multi
    def create(self, vals):
        field_without_prefix = vals['name'][2:]
        # guess field description
        field_description = re.sub(
            r'\w+', lambda m: m.group(0).capitalize(),
            field_without_prefix.replace('_id', '').replace('_', ' '))

        # Guess ttype
        # Don't execute as simple .get() in the dict to manage
        # correctly the type 'character varying(x)'
        ttype = False
        for k, v in self._SQL_MAPPING.items():
            if k in vals['sql_type']:
                ttype = v

        # Guess many2one_model_id
        many2one_model_id = False
        if vals['sql_type'] == 'integer' and(
                vals['name'][-3:] == '_id'):
            ttype = 'many2one'
            model_name = self._model_mapping().get(field_without_prefix, '')
            many2one_model_id = self.env['ir.model'].search(
                [('model', '=', model_name)]).id

        vals.update({
            'ttype': ttype,
            'field_description': field_description,
            'many2one_model_id': many2one_model_id,
        })
        return super(BiSQLViewField, self).create(vals)

    # Custom Section
    @api.model
    def _model_mapping(self):
        """Return dict of key value, to try to guess the model based on a
        field name. Sample :
        {'account_id': 'account.account'; 'product_id': 'product.product'}
        """
        relation_fields = self.env['ir.model.fields'].search([
            ('ttype', '=', 'many2one')])
        res = {}
        keys_to_pop = []
        for field in relation_fields:
            if field.name in res and res.get(field.name) != field.relation:
                # The field name is not predictive
                keys_to_pop.append(field.name)
            else:
                res.update({field.name: field.relation})

        for key in list(set(keys_to_pop)):
            res.pop(key)

        return res

    @api.multi
    def _prepare_model_field(self):
        self.ensure_one()
        return {
            'name': self.name,
            'field_description': self.field_description,
            'model_id': self.bi_sql_view_id.model_id.id,
            'ttype': self.ttype,
            'selection': self.ttype == 'selection' and self.selection or False,
            'relation': self.ttype == 'many2one' and
            self.many2one_model_id.model or False,
        }

    @api.multi
    def _prepare_tree_field(self):
        self.ensure_one()
        res = ''
        if self.field_description and self.tree_visibility != 'unavailable':
            res = """<field name="{}" {}/>""".format(
                self.name,
                self.tree_visibility == 'hidden' and 'invisible="1"' or '')
        return res

    @api.multi
    def _prepare_graph_field(self):
        self.ensure_one()
        res = ''
        if self.graph_type and self.field_description:
            res = """<field name="{}" type="{}" />""".format(
                self.name, self.graph_type)
        return res

    @api.multi
    def _prepare_pivot_field(self):
        self.ensure_one()
        res = ''
        if self.graph_type and self.field_description:
            res = """<field name="{}" type="{}" />""".format(
                self.name, self.graph_type)
        return res

    @api.multi
    def _prepare_search_field(self):
        self.ensure_one()
        res = ''
        if self.field_description:
            res = """<field name="{}"/>""".format(self.name)
        return res

    @api.multi
    def _prepare_search_filter_field(self):
        self.ensure_one()
        res = ''
        if self.field_description and self.is_group_by:
            res =\
                """<filter string="%s" context="{'group_by':'%s'}"/>""" % (
                    self.field_description, self.name)
        return res
