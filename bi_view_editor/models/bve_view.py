# -*- coding: utf-8 -*-
# Copyright 2015-2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from odoo import api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools.translate import _


class BveView(models.Model):
    _name = 'bve.view'
    _description = 'BI View Editor'

    @api.depends('group_ids')
    @api.multi
    def _compute_users(self):
        for bve_view in self:
            group_ids = bve_view.sudo().group_ids
            if group_ids:
                bve_view.user_ids = group_ids.mapped('users')
            else:
                bve_view.user_ids = self.env['res.users'].sudo().search([])

    @api.depends('name')
    @api.multi
    def _compute_model_name(self):
        for bve_view in self:
            name = [x for x in bve_view.name.lower() if x.isalnum()]
            model_name = ''.join(name).replace('_', '.').replace(' ', '.')
            bve_view.model_name = 'x_bve.' + model_name

    name = fields.Char(required=True, copy=False)
    model_name = fields.Char(compute='_compute_model_name', store=True)
    note = fields.Text(string='Notes')
    state = fields.Selection(
        [('draft', 'Draft'),
         ('created', 'Created')],
        default='draft',
        copy=False)
    data = fields.Serialized(
        help="Use the special query builder to define the query "
             "to generate your report dataset. "
             "NOTE: To be edited, the query should be in 'Draft' status.")
    action_id = fields.Many2one('ir.actions.act_window', string='Action')
    view_id = fields.Many2one('ir.ui.view', string='View')
    group_ids = fields.Many2many(
        'res.groups',
        string='Groups',
        help="User groups allowed to see the generated report; "
             "if NO groups are specified the report will be public "
             "for everyone.")
    user_ids = fields.Many2many(
        'res.users',
        string='Users',
        compute='_compute_users',
        store=True)

    _sql_constraints = [
        ('name_uniq',
         'unique(name)',
         _('Custom BI View names must be unique!')),
    ]

    @api.multi
    def _create_view_arch(self):
        self.ensure_one()

        def _get_field_def(name, def_type=''):
            if not def_type:
                return ''
            return """<field name="x_{}" type="{}" />""".format(
                name, def_type
            )

        def _get_field_type(field_info):
            row = field_info['row'] and 'row'
            column = field_info['column'] and 'col'
            measure = field_info['measure'] and 'measure'
            return row or column or measure

        def _get_field_list(fields_info):
            view_fields = []
            for field_info in fields_info:
                field_name = field_info['name']
                def_type = _get_field_type(field_info)
                if def_type:
                    field_def = _get_field_def(field_name, def_type)
                    view_fields.append(field_def)
            return view_fields

        fields_info = json.loads(self.data)
        view_fields = _get_field_list(fields_info)
        return view_fields

    @api.multi
    def _create_tree_view_arch(self):
        self.ensure_one()

        def _get_field_def(name):
            return """<field name="x_{}" />""".format(
                name
            )

        def _get_field_list(fields_info):
            view_fields = []
            for field_info in fields_info:
                field_name = field_info['name']
                if field_info['list'] and 'join_node' not in field_info:
                    field_def = _get_field_def(field_name)
                    view_fields.append(field_def)
            return view_fields

        fields_info = json.loads(self.data)

        view_fields = _get_field_list(fields_info)
        return view_fields

    @api.multi
    def _create_bve_view(self):
        self.ensure_one()

        # create views
        View = self.env['ir.ui.view']
        old_views = View.sudo().search([('model', '=', self.model_name)])
        old_views.sudo().unlink()

        view_vals = [{
            'name': 'Pivot Analysis',
            'type': 'pivot',
            'model': self.model_name,
            'priority': 16,
            'arch': """<?xml version="1.0"?>
                       <pivot string="Pivot Analysis">
                       {}
                       </pivot>
                    """.format("".join(self._create_view_arch()))
        }, {
            'name': 'Graph Analysis',
            'type': 'graph',
            'model': self.model_name,
            'priority': 16,
            'arch': """<?xml version="1.0"?>
                       <graph string="Graph Analysis"
                        type="bar" stacked="True">
                        {}
                       </graph>
                    """.format("".join(self._create_view_arch()))
        }, {
            'name': 'Search BI View',
            'type': 'search',
            'model': self.model_name,
            'priority': 16,
            'arch': """<?xml version="1.0"?>
                       <search string="Search BI View">
                       {}
                       </search>
                    """.format("".join(self._create_view_arch()))
        }]

        for vals in view_vals:
            View.sudo().create(vals)

        # create Tree view
        tree_view = View.sudo().create({
            'name': 'Tree Analysis',
            'type': 'tree',
            'model': self.model_name,
            'priority': 16,
            'arch': """<?xml version="1.0"?>
                       <tree string="List Analysis" create="false">
                       {}
                       </tree>
                    """.format("".join(self._create_tree_view_arch()))
            })

        # set the Tree view as the default one
        action_vals = {
            'name': self.name,
            'res_model': self.model_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,graph,pivot',
            'view_id': tree_view.id,
            'context': "{'service_name': '%s'}" % self.name,
        }

        ActWindow = self.env['ir.actions.act_window']
        action_id = ActWindow.sudo().create(action_vals)
        self.write({
            'action_id': action_id.id,
            'view_id': tree_view.id,
            'state': 'created'
        })

    @api.multi
    def _build_access_rules(self, model):
        self.ensure_one()

        def group_ids_with_access(model_name, access_mode):
            # pylint: disable=sql-injection
            self.env.cr.execute('''SELECT
                  g.id
                FROM
                  ir_model_access a
                  JOIN ir_model m ON (a.model_id=m.id)
                  JOIN res_groups g ON (a.group_id=g.id)
                  LEFT JOIN ir_module_category c ON (c.id=g.category_id)
                WHERE
                  m.model=%s AND
                  a.active IS True AND
                  a.perm_''' + access_mode, (model_name,))
            return [x[0] for x in self.env.cr.fetchall()]

        info = json.loads(self.data)
        model_names = list(set([f['model'] for f in info]))
        read_groups = set.intersection(*[set(
            group_ids_with_access(model_name, 'read')
        ) for model_name in model_names])

        # read access
        for group in read_groups:
            self.env['ir.model.access'].sudo().create({
                'name': 'read access to ' + self.model_name,
                'model_id': model.id,
                'group_id': group,
                'perm_read': True,
            })

        # read and write access
        for group in self.group_ids:
            self.env['ir.model.access'].sudo().create({
                'name': 'read-write access to ' + self.model_name,
                'model_id': model.id,
                'group_id': group.id,
                'perm_read': True,
                'perm_write': True,
            })

    @api.model
    def _create_sql_view(self):

        def get_fields_info(fields_data):
            fields_info = []
            for field_data in fields_data:
                field = self.env['ir.model.fields'].browse(field_data['id'])
                vals = {
                    'table': self.env[field.model_id.model]._table,
                    'table_alias': field_data['table_alias'],
                    'select_field': field.name,
                    'as_field': 'x_' + field_data['name'],
                    'join': False,
                    'model': field.model_id.model
                }
                if field_data.get('join_node'):
                    vals.update({'join': field_data['join_node']})
                fields_info.append(vals)
            return fields_info

        def get_join_nodes(info):
            join_nodes = [
                (f['table_alias'],
                 f['join'],
                 f['select_field']) for f in info if f['join'] is not False]
            return join_nodes

        def get_tables(info):
            tables = set([(f['table'], f['table_alias']) for f in info])
            return tables

        def get_fields(info):
            return [("{}.{}".format(f['table_alias'],
                                    f['select_field']),
                     f['as_field']) for f in info if 'join_node' not in f]

        def check_empty_data(data):
            if not data or data == '[]':
                raise UserError(_('No data to process.'))

        check_empty_data(self.data)

        formatted_data = json.loads(self.data)
        info = get_fields_info(formatted_data)
        select_fields = get_fields(info)
        tables = get_tables(info)
        join_nodes = get_join_nodes(info)

        table_name = self.model_name.replace('.', '_')

        # robustness in case something went wrong
        # pylint: disable=sql-injection
        self._cr.execute('DROP TABLE IF EXISTS "%s"' % table_name)

        basic_fields = [
            ("t0.id", "id")
        ]
        # pylint: disable=sql-injection
        q = """CREATE or REPLACE VIEW %s as (
            SELECT %s
            FROM  %s
            WHERE %s
            )""" % (table_name, ','.join(
            ["{} AS {}".format(f[0], f[1])
             for f in basic_fields + select_fields]), ','.join(
            ["{} AS {}".format(t[0], t[1])
             for t in list(tables)]), " AND ".join(
            ["{}.{} = {}.id".format(j[0], j[2], j[1])
             for j in join_nodes] + ["TRUE"]))

        self.env.cr.execute(q)

    @api.multi
    def action_create(self):
        self.ensure_one()

        def _prepare_field(field_data):
            if not field_data['custom']:
                field = self.env['ir.model.fields'].browse(field_data['id'])
                vals = {
                    'name': 'x_' + field_data['name'],
                    'complete_name': field.complete_name,
                    'model': self.model_name,
                    'relation': field.relation,
                    'field_description': field_data.get(
                        'description', field.field_description),
                    'ttype': field.ttype,
                    'selection': field.selection,
                    'size': field.size,
                    'state': 'manual'
                }
                if vals['ttype'] == 'monetary':
                    vals.update({'ttype': 'float'})
                if field.ttype == 'selection' and not field.selection:
                    model_obj = self.env[field.model_id.model]
                    selection = model_obj._fields[field.name].selection
                    if callable(selection):
                        selection_domain = selection(model_obj)
                    else:
                        selection_domain = selection
                    vals.update({'selection': str(selection_domain)})
                return vals

        # clean dirty view (in case something went wrong)
        self.action_reset()

        # create sql view
        self._create_sql_view()

        # create model and fields
        data = json.loads(self.data)
        model_vals = {
            'name': self.name,
            'model': self.model_name,
            'state': 'manual',
            'field_id': [
                (0, 0, _prepare_field(field))
                for field in data
                if 'join_node' not in field]
        }
        Model = self.env['ir.model'].sudo().with_context(bve=True)
        model = Model.create(model_vals)

        # give access rights
        self._build_access_rules(model)

        # create tree, graph and pivot views
        self._create_bve_view()

    @api.multi
    def open_view(self):
        self.ensure_one()
        [action] = self.action_id.read()
        action['display_name'] = _('BI View')
        return action

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_("%s (copy)") % self.name)
        return super(BveView, self).copy(default=default)

    @api.multi
    def action_reset(self):
        self.ensure_one()

        has_menus = False
        if self.action_id:
            action = 'ir.actions.act_window,%d' % (self.action_id.id,)
            menus = self.env['ir.ui.menu'].sudo().search(
                [('action', '=', action)]
            )
            has_menus = True if menus else False
            menus.sudo().unlink()

            if self.action_id.view_id:
                self.action_id.view_id.sudo().unlink()
            self.action_id.sudo().unlink()

        self.env['ir.ui.view'].sudo().search(
            [('model', '=', self.model_name)]).unlink()
        ir_models = self.env['ir.model'].sudo().search(
            [('model', '=', self.model_name)])
        for model in ir_models:
            model.sudo().unlink()

        table_name = self.model_name.replace('.', '_')
        tools.drop_view_if_exists(self.env.cr, table_name)

        self.state = 'draft'

        if has_menus:
            return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.multi
    def unlink(self):
        for view in self:
            if view.state == 'created':
                raise UserError(
                    _('You cannot delete a created view! '
                      'Reset the view to draft first.'))
        return super(BveView, self).unlink()
