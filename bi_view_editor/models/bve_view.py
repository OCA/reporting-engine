# -*- coding: utf-8 -*-
# Copyright 2015-2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import json

from openerp import api, fields, models, tools
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _


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

    name = fields.Char(required=True, copy=False)
    model_name = fields.Char()

    note = fields.Text(string='Notes')

    state = fields.Selection(
        [('draft', 'Draft'),
         ('created', 'Created')],
        default='draft',
        copy=False)
    data = fields.Text(
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
        compute=_compute_users,
        store=True)

    _sql_constraints = [
        ('name_uniq',
         'unique(name)',
         _('Custom BI View names must be unique!')),
    ]

    @api.multi
    def unlink(self):
        for view in self:
            if view.state == 'created':
                raise UserError(
                    _('You cannot delete a created view! '
                      'Reset the view to draft first.'))
        return super(BveView, self).unlink()

    @api.multi
    def action_reset(self):
        self.ensure_one()

        has_menus = False
        if self.action_id:
            menu_values = self.env['ir.values'].sudo().search([
                ('model', '=', 'ir.ui.menu'),
                ('key', '=', 'action'),
                ('key2', '=', 'tree_but_open'),
                ('value', '=', 'ir.actions.act_window,%d' % (self.action_id,))
            ])

            has_menus = True if menu_values else False
            menu_ids = []
            for menu_value in menu_values:
                if menu_value.res_id:
                    menu_ids.append(menu_value.res_id)
            menus = self.env['ir.ui.menu'].browse(menu_ids)
            menus.sudo().unlink()
            menu_values.sudo().unlink()
            wizard_menus = self.env['wizard.ir.model.menu.create'].search([
                ('menu_id', 'in', menu_ids)
            ])
            wizard_menus.sudo().unlink()

            if self.action_id.view_id:
                self.action_id.view_id.sudo().unlink()
            self.action_id.sudo().unlink()

        models = self.env['ir.model'].sudo().search(
            [('model', '=', self.model_name)])
        for model in models:
            model.sudo().unlink()

        table_name = self.model_name.replace('.', '_')
        tools.drop_view_if_exists(self.env.cr, table_name)

        self.state = 'draft'

        if has_menus:
            return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.multi
    def _create_view_arch(self):
        self.ensure_one()

        def _get_field_def(field_name, def_type):
            return """<field name="x_{}" type="{}" />""".format(
                field_name, def_type
            )

        def _get_field_type(field_info):
            row = field_info['row'] and 'row'
            column = field_info['column'] and 'col'
            measure = field_info['measure'] and 'measure'
            return row or column or measure

        fields_info = json.loads(self._get_format_data(self.data))
        view_fields = []
        for field_info in fields_info:
            field_name = field_info['name']
            def_type = _get_field_type(field_info)
            if def_type:
                field_def = _get_field_def(field_name, def_type)
                view_fields.append(field_def)
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
                if 'join_node' not in field_info:
                    if 'list' not in field_info or field_info['list']:
                        field_def = _get_field_def(field_name)
                        view_fields.append(field_def)
            return view_fields

        fields_info = json.loads(self._get_format_data(self.data))

        view_fields = _get_field_list(fields_info)
        return view_fields

    @api.model
    def _get_format_data(self, data):
        data = data.replace('\'', '"')
        data = data.replace(': u"', ':"')
        return data

    @api.multi
    def action_create(self):
        self.ensure_one()

        self._create_bve_object()
        self._create_bve_view()

    @api.multi
    def _create_bve_view(self):
        self.ensure_one()

        # create views
        View = self.env['ir.ui.view']
        old_views = View.sudo().search([('model', '=', self.model_name)])
        old_views.sudo().unlink()

        view_vals = {
            'name': 'Graph Analysis',
            'type': 'graph',
            'model': self.model_name,
            'priority': 16,
            'arch': """<?xml version="1.0"?>
                            <graph string="Graph Analysis"
                               type="pivot"
                               stacked="True"> {} </graph>
                         """.format("".join(self._create_view_arch()))
        }

        View.sudo().create(view_vals)

        # create Tree view
        tree_view = View.sudo().create(
            {'name': 'Tree Analysis',
             'type': 'tree',
             'model': self.model_name,
             'priority': 16,
             'arch': """<?xml version="1.0"?>
                        <tree string="List Analysis" create="false"> {} </tree>
                     """.format("".join(self._create_tree_view_arch()))
             })

        # set the Tree view as the default one
        action_vals = {
            'name': self.name,
            'res_model': self.model_name,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'tree,graph',
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
    def _create_bve_object(self):
        self.ensure_one()

        def _get_fields_info(fields_data):
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

        def _build_query():
            data = self.data
            if not data or data == '[]':
                raise UserError(_('No data to process.'))

            formatted_data = json.loads(self._get_format_data(data))
            info = _get_fields_info(formatted_data)
            fields = [("{}.{}".format(f['table_alias'],
                                      f['select_field']),
                       f['as_field']) for f in info if 'join_node' not in f]
            tables = set([(f['table'], f['table_alias']) for f in info])
            join_nodes = [
                (f['table_alias'],
                 f['join'],
                 f['select_field']) for f in info if f['join'] is not False]

            table_name = self.model_name.replace('.', '_')
            tools.drop_view_if_exists(self.env.cr, table_name)

            basic_fields = [
                ("t0.id", "id"),
                ("t0.write_uid", "write_uid"),
                ("t0.write_date", "write_date"),
                ("t0.create_uid", "create_uid"),
                ("t0.create_date", "create_date")
            ]

            q = """CREATE or REPLACE VIEW %s as (
                SELECT %s
                FROM  %s
                WHERE %s
                )""" % (table_name, ','.join(
                ["{} AS {}".format(f[0], f[1])
                 for f in basic_fields + fields]), ','.join(
                ["{} AS {}".format(t[0], t[1])
                 for t in list(tables)]), " AND ".join(
                ["{}.{} = {}.id".format(j[0], j[2], j[1])
                 for j in join_nodes] + ["TRUE"]))

            self.env.cr.execute(q)

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
                if field.ttype == 'selection' and not field.selection:
                    model_obj = self.env[field.model_id.model]
                    selection = model_obj._columns[field.name].selection
                    selection_domain = str(selection)
                    vals.update({'selection': selection_domain})
                return vals

        def _prepare_object():
            data = json.loads(self._get_format_data(self.data))
            return {
                'name': self.name,
                'model': self.model_name,
                'field_id': [
                    (0, 0, _prepare_field(field))
                    for field in data
                    if 'join_node' not in field]
            }

        def _build_object():
            vals = _prepare_object()
            Model = self.env['ir.model']
            res_id = Model.sudo().with_context(bve=True).create(vals)
            return res_id

        def group_ids_with_access(model_name, access_mode):
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

        def _build_access_rules(obj):
            info = json.loads(self._get_format_data(self.data))
            models = list(set([f['model'] for f in info]))
            read_groups = set.intersection(*[set(
                group_ids_with_access(model, 'read')) for model in models])

            # read access
            for group in read_groups:
                self.env['ir.model.access'].sudo().create({
                    'name': 'read access to ' + self.model_name,
                    'model_id': obj.id,
                    'group_id': group,
                    'perm_read': True,
                })

            # read and write access
            for group in self.group_ids:
                self.env['ir.model.access'].sudo().create({
                    'name': 'read-write access to ' + self.model_name,
                    'model_id': obj.id,
                    'group_id': group.id,
                    'perm_read': True,
                    'perm_write': True,
                })

        self.model_name = 'x_bve.' + ''.join(
            [x for x in self.name.lower()
             if x.isalnum()]).replace('_', '.').replace(' ', '.')
        _build_query()
        obj = _build_object()
        _build_access_rules(obj)

    @api.multi
    def open_view(self):
        self.ensure_one()
        return {
            'name': _('BI View'),
            'type': 'ir.actions.act_window',
            'res_model': self.model_name,
            'view_type': 'form',
            'view_mode': 'tree,graph',
        }

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_("%s (copy)") % self.name)
        return super(BveView, self).copy(default=default)
