# Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json
from psycopg2.extensions import AsIs

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class BveView(models.Model):
    _name = 'bve.view'
    _description = 'BI View Editor'

    @api.depends('group_ids', 'group_ids.users')
    def _compute_users(self):
        for bve_view in self.sudo():
            if bve_view.group_ids:
                bve_view.user_ids = bve_view.group_ids.mapped('users')
            else:
                bve_view.user_ids = self.env['res.users'].sudo().search([])

    @api.depends('name')
    def _compute_model_name(self):
        for bve_view in self:
            name = [x for x in bve_view.name.lower() if x.isalnum()]
            model_name = ''.join(name).replace('_', '.').replace(' ', '.')
            bve_view.model_name = 'x_bve.' + model_name

    def _compute_serialized_data(self):
        for bve_view in self:
            serialized_data = []
            for line in bve_view.line_ids.sorted(key=lambda r: r.sequence):
                serialized_data_dict = {
                    'sequence': line.sequence,
                    'model_id': line.model_id.id,
                    'id': line.field_id.id,
                    'name': line.name,
                    'model_name': line.model_id.name,
                    'model': line.model_id.model,
                    'type': line.ttype,
                    'table_alias': line.table_alias,
                    'description': line.description,
                    'row': line.row,
                    'column': line.column,
                    'measure': line.measure,
                    'list': line.in_list,
                }
                if line.join_node:
                    serialized_data_dict.update({
                        'join_node': line.join_node,
                        'relation': line.relation,
                    })
                serialized_data += [serialized_data_dict]
            bve_view.data = json.dumps(serialized_data)

    def _inverse_serialized_data(self):
        for bve_view in self:
            line_ids = self._sync_lines_and_data(bve_view.data)
            bve_view.write({'line_ids': line_ids})

    name = fields.Char(required=True, copy=False)
    model_name = fields.Char(compute='_compute_model_name', store=True)
    note = fields.Text(string='Notes')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('created', 'Created')
    ], default='draft', copy=False)
    data = fields.Char(
        compute='_compute_serialized_data',
        inverse='_inverse_serialized_data',
        help="Use the special query builder to define the query "
             "to generate your report dataset. "
             "NOTE: To be edited, the query should be in 'Draft' status.")
    line_ids = fields.One2many(
        'bve.view.line',
        'bve_view_id',
        string='Lines')
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
    query = fields.Text()

    _sql_constraints = [
        ('name_uniq',
         'unique(name)',
         _('Custom BI View names must be unique!')),
    ]

    @api.multi
    def _create_view_arch(self):
        self.ensure_one()

        def _get_field_def(name, def_type):
            return """<field name="{}" type="{}" />""".format(name, def_type)

        def _get_field_type(line):
            row = line.row and 'row'
            column = line.column and 'col'
            measure = line.measure and 'measure'
            return row or column or measure

        view_fields = []
        for line in self.line_ids:
            def_type = _get_field_type(line)
            if def_type:
                view_fields.append(_get_field_def(line.name, def_type))
        return view_fields

    @api.multi
    def _create_tree_view_arch(self):
        self.ensure_one()

        def _get_field_def(name):
            return """<field name="{}" />""".format(name)

        view_fields = []
        for line in self.line_ids:
            if line.in_list and not line.join_node:
                view_fields.append(_get_field_def(line.name))
        return view_fields

    @api.multi
    def _create_bve_view(self):
        self.ensure_one()

        # create views
        View = self.env['ir.ui.view']
        old_views = View.sudo().search([('model', '=', self.model_name)])
        old_views.unlink()

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

        View.sudo().create(view_vals)

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

        if not self.group_ids:
            self.env['ir.model.access'].sudo().create({
                'name': 'read access to ' + self.model_name,
                'model_id': model.id,
                'perm_read': True,
            })
        else:
            # read access only to model
            access_vals = []
            for group in self.group_ids:
                access_vals += [{
                    'name': 'read access to ' + self.model_name,
                    'model_id': model.id,
                    'group_id': group.id,
                    'perm_read': True
                }]
            self.env['ir.model.access'].sudo().create(access_vals)

    @api.multi
    def _create_sql_view(self):
        self.ensure_one()

        def get_fields_info(lines):
            fields_info = []
            for line in lines:
                vals = {
                    'table': self.env[line.field_id.model_id.model]._table,
                    'table_alias': line.table_alias,
                    'select_field': line.field_id.name,
                    'as_field': line.name,
                    'join': line.join_node,
                }
                fields_info.append(vals)
            return fields_info

        def get_join_nodes(info):
            return [(
                f['table_alias'],
                f['join'],
                f['select_field']
            ) for f in info if f['join']]

        def get_tables(info):
            return set([(f['table'], f['table_alias']) for f in info])

        def get_select_fields(info):
            first_field = [(info[0]['table_alias'] + ".id", "id")]
            next_fields = [
                ("{}.{}".format(f['table_alias'], f['select_field']),
                 f['as_field']) for f in info if 'join_node' not in f
            ]
            return first_field + next_fields

        if not self.line_ids:
            raise UserError(_('No data to process.'))

        info = get_fields_info(self.line_ids)
        select_fields = get_select_fields(info)
        tables = get_tables(info)
        join_nodes = get_join_nodes(info)

        view_name = self.model_name.replace('.', '_')
        select_str = ', '.join(["{} AS {}".format(f[0], f[1])
                                for f in select_fields])
        from_str = ', '.join(["{} AS {}".format(t[0], t[1])
                              for t in list(tables)])
        where_str = " AND ".join(["{}.{} = {}.id".format(j[0], j[2], j[1])
                                  for j in join_nodes])

        # robustness in case something went wrong
        self._cr.execute('DROP TABLE IF EXISTS %s', (AsIs(view_name), ))

        self.query = """
            SELECT %s

            FROM  %s
            """ % (AsIs(select_str), AsIs(from_str), )
        if where_str:
            self.query += """
            WHERE %s
            """ % (AsIs(where_str), )

        self.env.cr.execute(
            """CREATE or REPLACE VIEW %s as (
            %s
            )""", (AsIs(view_name), AsIs(self.query), ))

    @api.multi
    def action_translations(self):
        self.ensure_one()
        if self.state != 'created':
            return
        model = self.env['ir.model'].sudo().search([
            ('model', '=', self.model_name)
        ])
        IrTranslation = self.env['ir.translation'].sudo()
        IrTranslation.translate_fields('ir.model', model.id)
        for field_id in model.field_id.ids:
            IrTranslation.translate_fields('ir.model.fields', field_id)
        return {
            'name': 'Translations',
            'res_model': 'ir.translation',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_id': self.env.ref('base.view_translation_dialog_tree').id,
            'target': 'current',
            'flags': {'search_view': True, 'action_buttons': True},
            'domain': [
                '|',
                '&',
                ('res_id', 'in', model.field_id.ids),
                ('name', '=', 'ir.model.fields,field_description'),
                '&',
                ('res_id', '=', model.id),
                ('name', '=', 'ir.model,name')
            ],
        }

    @api.multi
    def action_create(self):
        self.ensure_one()

        def _prepare_field(line):
            field = line.field_id
            vals = {
                'name': line.name,
                'complete_name': field.complete_name,
                'model': self.model_name,
                'relation': field.relation,
                'field_description': line.description,
                'ttype': field.ttype,
                'selection': field.selection,
                'size': field.size,
                'state': 'manual',
                'readonly': True,
                'groups': [(6, 0, field.groups.ids)],
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

        self._check_invalid_lines()
        self._check_groups_consistency()

        # force removal of dirty views in case something went wrong
        self.sudo().action_reset()

        # create sql view
        self._create_sql_view()

        # create model and fields
        fields_data = self.line_ids.filtered(lambda l: not l.join_node)
        field_ids = [(0, 0, _prepare_field(f)) for f in fields_data]
        model = self.env['ir.model'].sudo().with_context(bve=True).create({
            'name': self.name,
            'model': self.model_name,
            'state': 'manual',
            'field_id': field_ids,
        })

        # give access rights
        self._build_access_rules(model)

        # create tree, graph and pivot views
        self._create_bve_view()

    def _check_groups_consistency(self):
        self.ensure_one()

        if not self.group_ids:
            return

        for line_model in self.line_ids.mapped('model_id'):
            res_count = self.env['ir.model.access'].sudo().search([
                ('model_id', '=', line_model.id),
                ('perm_read', '=', True),
                '|',
                ('group_id', '=', False),
                ('group_id', 'in', self.group_ids.ids),
            ], limit=1)
            if not res_count:
                access_records = self.env['ir.model.access'].sudo().search([
                    ('model_id', '=', line_model.id),
                    ('perm_read', '=', True),
                ])
                group_list = ''
                for group in access_records.mapped('group_id'):
                    group_list += ' * %s\n' % (group.full_name, )
                msg_title = _(
                    'The model "%s" cannot be accessed by users with the '
                    'selected groups only.' % (line_model.name, ))
                msg_details = _(
                    'At least one of the following groups must be added:')
                raise UserError(_(
                    '%s\n\n%s\n%s' % (msg_title, msg_details, group_list,)
                ))

    def _check_invalid_lines(self):
        self.ensure_one()
        if any(not line.model_id for line in self.line_ids):
            invalid_lines = self.line_ids.filtered(lambda l: not l.model_id)
            missing_models = set(invalid_lines.mapped('model_name'))
            missing_models = ', '.join(missing_models)
            raise UserError(_(
                'Following models are missing: %s.\n'
                'Probably some modules were uninstalled.' % (missing_models,)
            ))
        if any(not line.field_id for line in self.line_ids):
            invalid_lines = self.line_ids.filtered(lambda l: not l.field_id)
            missing_fields = set(invalid_lines.mapped('field_name'))
            missing_fields = ', '.join(missing_fields)
            raise UserError(_(
                'Following fields are missing: %s.' % (missing_fields,)
            ))

    @api.multi
    def open_view(self):
        self.ensure_one()
        self._check_invalid_lines()
        [action] = self.action_id.read()
        action['display_name'] = _('BI View')
        return action

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_("%s (copy)") % self.name)
        return super().copy(default=default)

    @api.multi
    def action_reset(self):
        self.ensure_one()

        has_menus = False
        if self.action_id:
            action = 'ir.actions.act_window,%d' % (self.action_id.id,)
            menus = self.env['ir.ui.menu'].search([
                ('action', '=', action)
            ])
            has_menus = True if menus else False
            menus.unlink()

            if self.action_id.view_id:
                self.sudo().action_id.view_id.unlink()
            self.sudo().action_id.unlink()

        self.env['ir.ui.view'].sudo().search(
            [('model', '=', self.model_name)]).unlink()
        models_to_delete = self.env['ir.model'].sudo().search([
            ('model', '=', self.model_name)])
        if models_to_delete:
            models_to_delete.unlink()

        table_name = self.model_name.replace('.', '_')
        tools.drop_view_if_exists(self.env.cr, table_name)

        self.state = 'draft'

        if has_menus:
            return {'type': 'ir.actions.client', 'tag': 'reload'}

    @api.multi
    def unlink(self):
        if self.filtered(lambda v: v.state == 'created'):
            raise UserError(
                _('You cannot delete a created view! '
                  'Reset the view to draft first.'))
        return super().unlink()

    @api.model
    def _sync_lines_and_data(self, data):
        line_ids = [(5, 0, 0)]
        fields_info = {}
        if data:
            fields_info = json.loads(data)

        table_model_map = {}
        for item in fields_info:
            if item.get('join_node', -1) == -1:
                table_model_map[item['table_alias']] = item['model_id']

        for sequence, field_info in enumerate(fields_info, start=1):
            join_model_id = False
            join_node = field_info.get('join_node', -1)
            if join_node != -1 and table_model_map.get(join_node):
                join_model_id = int(table_model_map[join_node])

            line_ids += [(0, False, {
                'sequence': sequence,
                'model_id': field_info['model_id'],
                'table_alias': field_info['table_alias'],
                'description': field_info['description'],
                'field_id': field_info['id'],
                'ttype': field_info['type'],
                'row': field_info['row'],
                'column': field_info['column'],
                'measure': field_info['measure'],
                'in_list': field_info['list'],
                'relation': field_info.get('relation'),
                'join_node': field_info.get('join_node'),
                'join_model_id': join_model_id,
            })]
        return line_ids

    @api.constrains('line_ids')
    def _constraint_line_ids(self):
        for view in self:
            nodes = view.line_ids.filtered(lambda n: n.join_node)
            nodes_models = nodes.mapped('table_alias')
            nodes_models += nodes.mapped('join_node')
            not_nodes = view.line_ids.filtered(lambda n: not n.join_node)
            not_nodes_models = not_nodes.mapped('table_alias')
            err_msg = _('Inconsistent lines.')
            if set(nodes_models) - set(not_nodes_models):
                raise ValidationError(err_msg)
            if len(set(not_nodes_models) - set(nodes_models)) > 1:
                raise ValidationError(err_msg)

    @api.model
    def get_clean_list(self, data_dict):
        serialized_data = json.loads(data_dict)
        table_alias_list = set()
        for item in serialized_data:
            if item.get('join_node', -1) == -1:
                table_alias_list.add(item['table_alias'])

        for item in serialized_data:
            if item.get('join_node', -1) != -1:
                if item['table_alias'] not in table_alias_list:
                    serialized_data.remove(item)
                elif item['join_node'] not in table_alias_list:
                    serialized_data.remove(item)

        return json.dumps(serialized_data)
