# -*- coding: utf-8 -*-
# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from psycopg2 import ProgrammingError

from openerp import _, api, fields, models, SUPERUSER_ID
from openerp.exceptions import Warning as UserError

_logger = logging.getLogger(__name__)


class BiSQLView(models.Model):
    _name = 'bi.sql.view'
    _inherit = ['sql.request.mixin']

    _sql_prefix = 'x_bi_sql_view_'

    _model_prefix = 'x_bi_sql_view.'

    _sql_request_groups_relation = 'bi_sql_view_groups_rel'

    _sql_request_users_relation = 'bi_sql_view_users_rel'

    _STATE_SQL_EDITOR = [
        ('model_valid', 'SQL View and Model Created'),
        ('ui_valid', 'Graph, action and Menu Created'),
    ]

    technical_name = fields.Char(
        string='Technical Name', required=True,
        help="Suffix of the SQL view. (SQL full name will be computed and"
        " prefixed by 'x_bi_sql_view_'. Should have correct"
        "syntax. For more information, see https://www.postgresql.org/"
        "docs/current/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS")

    view_name = fields.Char(
        string='View Name', compute='_compute_view_name', readonly=True,
        store=True, help="Full name of the SQL view")

    model_name = fields.Char(
        string='Model Name', compute='_compute_model_name', readonly=True,
        store=True, help="Full Qualified Name of the transient model that will"
        " be created.")

    is_materialized = fields.Boolean(
        string='Is Materialized View', default=True, readonly=True,
        states={'draft': [('readonly', False)]})

    materialized_text = fields.Char(
        compute='_compute_materialized_text', store=True)

    size = fields.Char(
        string='Database Size', readonly=True,
        help="Size of the materialized view and its indexes")

    state = fields.Selection(selection_add=_STATE_SQL_EDITOR)

    query = fields.Text(
        help="SQL Request that will be inserted as the view. Take care to :\n"
        " * set a name for all your selected fields, specially if you use"
        " SQL function (like EXTRACT, ...);\n"
        " * Do not use 'SELECT *' or 'SELECT table.*';\n"
        " * prefix the name of the selectable columns by 'x_';",
        default="SELECT\n"
        "    my_field as x_my_field\n"
        "FROM my_table")

    domain_force = fields.Text(
        string='Extra Rule Definition', default="[]", help="Define here"
        " access restriction to data.\n"
        " Take care to use field name prefixed by 'x_'."
        " A global 'ir.rule' will be created."
        " A typical Multi Company rule is for exemple \n"
        " ['|', ('x_company_id','child_of', [user.company_id.id]),"
        "('x_company_id','=',False)].")

    has_group_changed = fields.Boolean(copy=False)

    bi_sql_view_field_ids = fields.One2many(
        string='SQL Fields', comodel_name='bi.sql.view.field',
        inverse_name='bi_sql_view_id')

    model_id = fields.Many2one(
        string='Odoo Model', comodel_name='ir.model', readonly=True)

    graph_view_id = fields.Many2one(
        string='Odoo Graph View', comodel_name='ir.ui.view', readonly=True)

    search_view_id = fields.Many2one(
        string='Odoo Search View', comodel_name='ir.ui.view', readonly=True)

    action_id = fields.Many2one(
        string='Odoo Action', comodel_name='ir.actions.act_window',
        readonly=True)

    menu_id = fields.Many2one(
        string='Odoo Menu', comodel_name='ir.ui.menu', readonly=True)

    cron_id = fields.Many2one(
        string='Odoo Cron', comodel_name='ir.cron', readonly=True,
        help="Cron Task that will refresh the materialized view")

    rule_id = fields.Many2one(
        string='Odoo Rule', comodel_name='ir.rule', readonly=True)

    # Compute Section
    @api.depends('is_materialized')
    @api.multi
    def _compute_materialized_text(self):
        for sql_view in self:
            sql_view.materialized_text =\
                sql_view.is_materialized and 'MATERIALIZED' or ''

    @api.depends('technical_name')
    @api.multi
    def _compute_view_name(self):
        for sql_view in self:
            sql_view.view_name = '%s%s' % (
                sql_view._sql_prefix, sql_view.technical_name)

    @api.depends('technical_name')
    @api.multi
    def _compute_model_name(self):
        for sql_view in self:
            sql_view.model_name = '%s%s' % (
                sql_view._model_prefix, sql_view.technical_name)

    @api.onchange('group_ids')
    def onchange_group_ids(self):
        if self.state not in ('draft', 'sql_valid'):
            self.has_group_changed = True

    # Overload Section
    @api.multi
    def unlink(self):
        non_draft_views = self.search([
            ('id', 'in', self.ids),
            ('state', 'not in', ('draft', 'sql_valid'))])
        if non_draft_views:
            raise UserError(_("You can only unlink draft views"))
        return self.unlink()

    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default.update({
            'name': _('%s (Copy)') % (self.name),
            'technical_name': '%s_copy' % (self.technical_name),
        })
        return super(BiSQLView, self).copy(default=default)

    # Action Section
    @api.multi
    def button_create_sql_view_and_model(self):
        for sql_view in self:
            if sql_view.state != 'sql_valid':
                raise UserError(_(
                    "You can only process this action on SQL Valid items"))
            # Create ORM and acess
            sql_view._create_model_and_fields()
            sql_view._create_model_access()

            # Create SQL View and indexes
            sql_view._create_view()
            sql_view._create_index()

            if sql_view.is_materialized:
                sql_view.cron_id = self.env['ir.cron'].create(
                    sql_view._prepare_cron()).id
            sql_view.state = 'model_valid'

    @api.multi
    def button_set_draft(self):
        for sql_view in self:
            if sql_view.state in ('model_valid', 'ui_valid'):
                # Drop SQL View (and indexes by cascade)
                sql_view._drop_view()

                # Drop ORM
                sql_view._drop_model_and_fields()

            sql_view.graph_view_id.unlink()
            sql_view.action_id.unlink()
            sql_view.menu_id.unlink()
            sql_view.rule_id.unlink()
            if sql_view.cron_id:
                sql_view.cron_id.unlink()
            sql_view.write({'state': 'draft', 'has_group_changed': False})

    @api.multi
    def button_create_ui(self):
        self.graph_view_id = self.env['ir.ui.view'].create(
            self._prepare_graph_view()).id
        self.search_view_id = self.env['ir.ui.view'].create(
            self._prepare_search_view()).id
        self.action_id = self.env['ir.actions.act_window'].create(
            self._prepare_action()).id
        self.menu_id = self.env['ir.ui.menu'].create(
            self._prepare_menu()).id
        self.write({'state': 'ui_valid'})

    @api.multi
    def button_update_model_access(self):
        self._drop_model_access()
        self._create_model_access()
        self.write({'has_group_changed': False})

    @api.multi
    def button_refresh_materialized_view(self):
        self._refresh_materialized_view()

    @api.multi
    def button_open_view(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': self.model_id.model,
            'view_id': self.graph_view_id.id,
            'search_view_id': self.search_view_id.id,
            'view_type': 'graph',
            'view_mode': 'graph',
        }

    # Prepare Function
    @api.multi
    def _prepare_model(self):
        self.ensure_one()
        field_id = []
        for field in self.bi_sql_view_field_ids.filtered(
                lambda x: x.field_description is not False):
            field_id.append([0, False, field._prepare_model_field()])
        return {
            'name': self.name,
            'model': self.model_name,
            'access_ids': [],
            'field_id': field_id,
        }

    @api.multi
    def _prepare_model_access(self):
        self.ensure_one()
        res = []
        for group in self.group_ids:
            res.append({
                'name': _('%s Access %s') % (
                    self.model_name, group.full_name),
                'model_id': self.model_id.id,
                'group_id': group.id,
                'perm_read': True,
                'perm_create': False,
                'perm_write': False,
                'perm_unlink': False,
            })
        return res

    @api.multi
    def _prepare_cron(self):
        self.ensure_one()
        return {
            'name': _('Refresh Materialized View %s') % (self.view_name),
            'user_id': SUPERUSER_ID,
            'model': 'bi.sql.view',
            'function': 'button_refresh_materialized_view',
            'args': repr(([self.id],))
        }

    @api.multi
    def _prepare_rule(self):
        self.ensure_one()
        return {
            'name': _('Access %s') % (self.name),
            'model_id': self.model_id.id,
            'domain_force': self.domain_force,
            'global': True,
        }

    @api.multi
    def _prepare_graph_view(self):
        self.ensure_one()
        return {
            'name': self.name,
            'type': 'graph',
            'model': self.model_id.model,
            'arch':
                """<?xml version="1.0"?>"""
                """<graph string="Analysis" type="pivot" stacked="True">{}"""
                """</graph>""".format("".join(
                    [x._prepare_graph_field()
                        for x in self.bi_sql_view_field_ids]))
        }

    @api.multi
    def _prepare_search_view(self):
        self.ensure_one()
        return {
            'name': self.name,
            'type': 'search',
            'model': self.model_id.model,
            'arch':
                """<?xml version="1.0"?>"""
                """<search string="Analysis">{}"""
                """<group expand="1" string="Group By">{}</group>"""
                """</search>""".format(
                    "".join(
                        [x._prepare_search_field()
                            for x in self.bi_sql_view_field_ids]),
                    "".join(
                        [x._prepare_search_filter_field()
                            for x in self.bi_sql_view_field_ids]))
        }

    @api.multi
    def _prepare_action(self):
        self.ensure_one()
        return {
            'name': self.name,
            'res_model': self.model_id.model,
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'graph',
            'view_id': self.graph_view_id.id,
            'search_view_id': self.search_view_id.id,
        }

    @api.multi
    def _prepare_menu(self):
        self.ensure_one()
        return {
            'name': self.name,
            'parent_id': self.env.ref('bi_sql_editor.menu_bi_sql_editor').id,
            'action': 'ir.actions.act_window,%s' % (self.action_id.id),
        }

    # Custom Section
    def _log_execute(self, req):
        _logger.info("Executing SQL Request %s ..." % (req))
        self.env.cr.execute(req)

    @api.multi
    def _drop_view(self):
        for sql_view in self:
            self._log_execute(
                "DROP %s VIEW IF EXISTS %s" % (
                    sql_view.materialized_text, sql_view.view_name))
            sql_view.size = False

    @api.multi
    def _create_view(self):
        for sql_view in self:
            sql_view._drop_view()
            try:
                self._log_execute(sql_view._prepare_request_for_execution())
                sql_view._refresh_size()
            except ProgrammingError as e:
                raise UserError(_(
                    "SQL Error while creating %s VIEW %s :\n %s") % (
                        sql_view.materialized_text, sql_view.view_name,
                        e.message))

    @api.multi
    def _create_index(self):
        for sql_view in self:
            for sql_field in sql_view.bi_sql_view_field_ids.filtered(
                    lambda x: x.is_index is True):
                self._log_execute(
                    "CREATE INDEX %s ON %s (%s);" % (
                        sql_field.index_name, sql_view.view_name,
                        sql_field.name))

    @api.multi
    def _create_model_and_fields(self):
        for sql_view in self:
            # Create model
            sql_view.model_id = self.env['ir.model'].create(
                self._prepare_model()).id
            sql_view.rule_id = self.env['ir.rule'].create(
                self._prepare_rule()).id
            # Drop table, created by the ORM
            req = "DROP TABLE %s" % (sql_view.view_name)
            self.env.cr.execute(req)

    @api.multi
    def _create_model_access(self):
        for sql_view in self:
            for item in sql_view._prepare_model_access():
                self.env['ir.model.access'].create(item)

    @api.multi
    def _drop_model_access(self):
        for sql_view in self:
            self.env['ir.model.access'].search(
                [('model_id', '=', sql_view.model_name)]).unlink()

    @api.multi
    def _drop_model_and_fields(self):
        for sql_view in self:
            sql_view.model_id.unlink()

    @api.multi
    def _hook_executed_request(self):
        self.ensure_one()
        req = """
            SELECT  attnum,
                    attname AS column,
                    format_type(atttypid, atttypmod) AS type
            FROM    pg_attribute
            WHERE   attrelid = '%s'::regclass
            AND     NOT attisdropped
            AND     attnum > 0
            ORDER   BY attnum;""" % (self.view_name)
        self.env.cr.execute(req)
        return self.env.cr.fetchall()

    @api.multi
    def _prepare_request_check_execution(self):
        self.ensure_one()
        return "CREATE VIEW %s AS (%s);" % (self.view_name, self.query)

    @api.multi
    def _prepare_request_for_execution(self):
        self.ensure_one()
        query = """
            SELECT
                CAST(row_number() OVER () as integer) AS id,
                CAST(Null as timestamp without time zone) as create_date,
                CAST(Null as integer) as create_uid,
                CAST(Null as timestamp without time zone) as write_date,
                CAST(Null as integer) as write_uid,
                my_query.*
            FROM
                (%s) as my_query
        """ % (self.query)
        return "CREATE %s VIEW %s AS (%s);" % (
            self.materialized_text, self.view_name, query)

    @api.multi
    def _check_execution(self):
        """Ensure that the query is valid, trying to execute it.
        a non materialized view is created for this check.
        A rollback is done at the end.
        After the execution, and before the rollback, an analysis of
        the database structure is done, to know fields type."""
        self.ensure_one()
        sql_view_field_obj = self.env['bi.sql.view.field']
        columns = super(BiSQLView, self)._check_execution()
        field_ids = []
        for column in columns:
            existing_field = self.bi_sql_view_field_ids.filtered(
                lambda x: x.name == column[1])
            if existing_field:
                # Update existing field
                field_ids.append(existing_field.id)
                existing_field.write({
                    'sequence': column[0],
                    'sql_type': column[2],
                })
            else:
                # Create a new one if name is prefixed by x_
                if column[1][:2] == 'x_':
                    field_ids.append(sql_view_field_obj.create({
                        'sequence': column[0],
                        'name': column[1],
                        'sql_type': column[2],
                        'bi_sql_view_id': self.id,
                    }).id)

        # Drop obsolete view field
        self.bi_sql_view_field_ids.filtered(
            lambda x: x.id not in field_ids).unlink()

        if not self.bi_sql_view_field_ids:
            raise UserError(_(
                "No Column was found.\n"
                "Columns name should be prefixed by 'x_'."))

        return columns

    @api.multi
    def _refresh_materialized_view(self):
        for sql_view in self:
            req = "REFRESH %s VIEW %s" % (
                sql_view.materialized_text, sql_view.view_name)
            self._log_execute(req)
            sql_view._refresh_size()

    @api.multi
    def _refresh_size(self):
        for sql_view in self:
            req = "SELECT pg_size_pretty(pg_total_relation_size('%s'));" % (
                sql_view.view_name)
            self.env.cr.execute(req)
            sql_view.size = self.env.cr.fetchone()[0]
