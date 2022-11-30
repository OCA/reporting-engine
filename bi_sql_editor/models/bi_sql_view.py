# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from datetime import datetime, timedelta

from psycopg2 import ProgrammingError

from odoo import SUPERUSER_ID, _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools import pycompat, sql, table_columns
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.models.ir_model import IrModel

_logger = logging.getLogger(__name__)


@api.model
def _instanciate(self, model_data):
    """Return a class for the custom model given by
    parameters ``model_data``."""
    # This monkey patch is meant to avoid create/search tables for those
    # materialized views. Doing "super" doesn't work.
    class CustomModel(models.Model):
        _name = pycompat.to_text(model_data["model"])
        _description = model_data["name"]
        _module = False
        _custom = True
        _transient = bool(model_data["transient"])
        __doc__ = model_data["info"]

    # START OF patch
    if model_data["model"].startswith(BiSQLView._model_prefix):
        CustomModel._auto = False
        CustomModel._abstract = True
    # END of patch
    return CustomModel


IrModel._instanciate = _instanciate


class BiSQLView(models.Model):
    _name = "bi.sql.view"
    _description = "BI SQL View"
    _order = "sequence"
    _inherit = ["sql.request.mixin"]

    _sql_prefix = "x_bi_sql_view_"

    _model_prefix = "x_bi_sql_view."

    _sql_request_groups_relation = "bi_sql_view_groups_rel"

    _sql_request_users_relation = "bi_sql_view_users_rel"

    _STATE_SQL_EDITOR = [
        ("model_valid", "SQL View and Model Created"),
        ("ui_valid", "Views, Action and Menu Created"),
    ]

    technical_name = fields.Char(
        string="Technical Name",
        required=True,
        help="Suffix of the SQL view. SQL full name will be computed and"
        " prefixed by 'x_bi_sql_view_'. Syntax should follow: "
        "https://www.postgresql.org/"
        "docs/current/static/sql-syntax-lexical.html#SQL-SYNTAX-IDENTIFIERS",
    )

    view_name = fields.Char(
        string="View Name",
        compute="_compute_view_name",
        readonly=True,
        store=True,
        help="Full name of the SQL view",
    )

    model_name = fields.Char(
        string="Model Name",
        compute="_compute_model_name",
        readonly=True,
        store=True,
        help="Full Qualified Name of the transient model that will" " be created.",
    )

    is_materialized = fields.Boolean(
        string="Is Materialized View",
        default=True,
        readonly=True,
        states={"draft": [("readonly", False)], "sql_valid": [("readonly", False)]},
    )

    materialized_text = fields.Char(compute="_compute_materialized_text", store=True)

    size = fields.Char(
        string="Database Size",
        readonly=True,
        help="Size of the materialized view and its indexes",
    )

    state = fields.Selection(selection_add=_STATE_SQL_EDITOR)

    view_order = fields.Char(
        string="View Order",
        required=True,
        readonly=False,
        states={"ui_valid": [("readonly", True)]},
        default="pivot,graph,tree",
        help="Comma-separated text. Possible values:" ' "graph", "pivot" or "tree"',
    )

    query = fields.Text(
        help="SQL Request that will be inserted as the view. Take care to :\n"
        " * set a name for all your selected fields, specially if you use"
        " SQL function (like EXTRACT, ...);\n"
        " * Do not use 'SELECT *' or 'SELECT table.*';\n"
        " * prefix the name of the selectable columns by 'x_';",
        default="SELECT\n" "    my_field as x_my_field\n" "FROM my_table",
    )

    domain_force = fields.Text(
        string="Extra Rule Definition",
        default="[]",
        readonly=True,
        help="Define here access restriction to data.\n"
        " Take care to use field name prefixed by 'x_'."
        " A global 'ir.rule' will be created."
        " A typical Multi Company rule is for exemple \n"
        " ['|', ('x_company_id','child_of', [user.company_id.id]),"
        "('x_company_id','=',False)].",
        states={"draft": [("readonly", False)], "sql_valid": [("readonly", False)]},
    )

    computed_action_context = fields.Text(
        compute="_compute_computed_action_context", string="Computed Action Context"
    )

    action_context = fields.Text(
        string="Action Context",
        default="{}",
        readonly=True,
        help="Define here a context that will be used"
        " by default, when creating the action.",
        states={
            "draft": [("readonly", False)],
            "sql_valid": [("readonly", False)],
            "model_valid": [("readonly", False)],
        },
    )

    has_group_changed = fields.Boolean(copy=False)

    bi_sql_view_field_ids = fields.One2many(
        string="SQL Fields",
        comodel_name="bi.sql.view.field",
        inverse_name="bi_sql_view_id",
    )

    model_id = fields.Many2one(
        string="Odoo Model", comodel_name="ir.model", readonly=True
    )

    tree_view_id = fields.Many2one(
        string="Odoo Tree View", comodel_name="ir.ui.view", readonly=True
    )

    graph_view_id = fields.Many2one(
        string="Odoo Graph View", comodel_name="ir.ui.view", readonly=True
    )

    pivot_view_id = fields.Many2one(
        string="Odoo Pivot View", comodel_name="ir.ui.view", readonly=True
    )

    search_view_id = fields.Many2one(
        string="Odoo Search View", comodel_name="ir.ui.view", readonly=True
    )

    action_id = fields.Many2one(
        string="Odoo Action", comodel_name="ir.actions.act_window", readonly=True
    )

    menu_id = fields.Many2one(
        string="Odoo Menu", comodel_name="ir.ui.menu", readonly=True
    )

    cron_id = fields.Many2one(
        string="Odoo Cron",
        comodel_name="ir.cron",
        readonly=True,
        help="Cron Task that will refresh the materialized view",
    )

    rule_id = fields.Many2one(string="Odoo Rule", comodel_name="ir.rule", readonly=True)

    group_ids = fields.Many2many(
        comodel_name="res.groups",
        readonly=True,
        states={"draft": [("readonly", False)], "sql_valid": [("readonly", False)]},
    )

    sequence = fields.Integer(string="sequence")

    # Constrains Section
    @api.constrains("is_materialized")
    def _check_index_materialized(self):
        for rec in self.filtered(lambda x: not x.is_materialized):
            if rec.bi_sql_view_field_ids.filtered(lambda x: x.is_index):
                raise UserError(
                    _("You can not create indexes on non materialized views")
                )

    @api.constrains("view_order")
    def _check_view_order(self):
        for rec in self:
            if rec.view_order:
                for vtype in rec.view_order.split(","):
                    if vtype not in ("graph", "pivot", "tree"):
                        raise UserError(
                            _("Only graph, pivot or tree views are supported")
                        )

    # Compute Section
    @api.depends("bi_sql_view_field_ids.graph_type")
    def _compute_computed_action_context(self):
        for rec in self:
            action = {
                "pivot_measures": [],
                "pivot_row_groupby": [],
                "pivot_column_groupby": [],
            }
            for field in rec.bi_sql_view_field_ids.filtered(
                lambda x: x.graph_type == "measure"
            ):
                action["pivot_measures"].append(field.name)

            for field in rec.bi_sql_view_field_ids.filtered(
                lambda x: x.graph_type == "row"
            ):
                action["pivot_row_groupby"].append(field.name)

            for field in rec.bi_sql_view_field_ids.filtered(
                lambda x: x.graph_type == "col"
            ):
                action["pivot_column_groupby"].append(field.name)

            rec.computed_action_context = str(action)

    @api.depends("is_materialized")
    def _compute_materialized_text(self):
        for sql_view in self:
            sql_view.materialized_text = (
                sql_view.is_materialized and "MATERIALIZED" or ""
            )

    @api.depends("technical_name")
    def _compute_view_name(self):
        for sql_view in self:
            sql_view.view_name = "{}{}".format(
                sql_view._sql_prefix,
                sql_view.technical_name,
            )

    @api.depends("technical_name")
    def _compute_model_name(self):
        for sql_view in self:
            sql_view.model_name = "{}{}".format(
                sql_view._model_prefix,
                sql_view.technical_name,
            )

    @api.onchange("group_ids")
    def onchange_group_ids(self):
        if self.state not in ("draft", "sql_valid"):
            self.has_group_changed = True

    # Overload Section
    def write(self, vals):
        res = super().write(vals)
        if vals.get("sequence", False):
            for rec in self.filtered(lambda x: x.menu_id):
                rec.menu_id.sequence = rec.sequence
        return res

    def unlink(self):
        if any(view.state not in ("draft", "sql_valid") for view in self):
            raise UserError(
                _(
                    "You can only unlink draft views."
                    "If you want to delete them, first set them to draft."
                )
            )
        if self.mapped("cron_id"):
            self.mapped("cron_id").unlink()
        return super().unlink()

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {})
        default.update(
            {
                "name": _("%s (Copy)") % self.name,
                "technical_name": "%s_copy" % self.technical_name,
            }
        )
        return super().copy(default=default)

    # Action Section
    def button_create_sql_view_and_model(self):
        for sql_view in self.filtered(lambda x: x.state == "sql_valid"):
            # Create ORM and access
            sql_view._create_model_and_fields()
            sql_view._create_model_access()

            # Create SQL View and indexes
            sql_view._create_view()
            sql_view._create_index()

            if sql_view.is_materialized:
                if not sql_view.cron_id:
                    sql_view.cron_id = (
                        self.env["ir.cron"].create(sql_view._prepare_cron()).id
                    )
                else:
                    sql_view.cron_id.active = True
            sql_view.state = "model_valid"

    def button_set_draft(self):
        for sql_view in self.filtered(lambda x: x.state != "draft"):
            sql_view.menu_id.unlink()
            sql_view.action_id.unlink()
            sql_view.tree_view_id.unlink()
            sql_view.graph_view_id.unlink()
            sql_view.pivot_view_id.unlink()
            sql_view.search_view_id.unlink()

            if sql_view.state in ("model_valid", "ui_valid"):
                # Drop SQL View (and indexes by cascade)
                if sql_view.is_materialized:
                    sql_view._drop_view()

                if sql_view.cron_id:
                    sql_view.cron_id.active = False

                # Drop ORM
                sql_view._drop_model_and_fields()

            sql_view.has_group_changed = False
            super(BiSQLView, sql_view).button_set_draft()
        return True

    def button_create_ui(self):
        self.tree_view_id = self.env["ir.ui.view"].create(self._prepare_tree_view()).id
        self.graph_view_id = (
            self.env["ir.ui.view"].create(self._prepare_graph_view()).id
        )
        self.pivot_view_id = (
            self.env["ir.ui.view"].create(self._prepare_pivot_view()).id
        )
        self.search_view_id = (
            self.env["ir.ui.view"].create(self._prepare_search_view()).id
        )
        self.action_id = (
            self.env["ir.actions.act_window"].create(self._prepare_action()).id
        )
        self.menu_id = self.env["ir.ui.menu"].create(self._prepare_menu()).id
        self.write({"state": "ui_valid"})

    def button_update_model_access(self):
        self._drop_model_access()
        self._create_model_access()
        self.write({"has_group_changed": False})

    def button_refresh_materialized_view(self):
        self._refresh_materialized_view()

    def button_open_view(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": self.model_id.model,
            "search_view_id": self.search_view_id.id,
            "view_mode": self.action_id.view_mode,
        }

    # Prepare Function
    def _prepare_model(self):
        self.ensure_one()
        field_id = []
        for field in self.bi_sql_view_field_ids.filtered(
            lambda x: x.field_description is not False
        ):
            field_id.append([0, False, field._prepare_model_field()])
        return {
            "name": self.name,
            "model": self.model_name,
            "access_ids": [],
            "field_id": field_id,
        }

    def _prepare_model_access(self):
        self.ensure_one()
        res = []
        for group in self.group_ids:
            res.append(
                {
                    "name": _("%s Access %s") % (self.model_name, group.full_name),
                    "model_id": self.model_id.id,
                    "group_id": group.id,
                    "perm_read": True,
                    "perm_create": False,
                    "perm_write": False,
                    "perm_unlink": False,
                }
            )
        return res

    def _prepare_cron(self):
        now = datetime.now()
        return {
            "name": _("Refresh Materialized View %s") % self.view_name,
            "user_id": SUPERUSER_ID,
            "model_id": self.env["ir.model"]
            .search([("model", "=", self._name)], limit=1)
            .id,
            "state": "code",
            "code": "model._refresh_materialized_view_cron(%s)" % self.ids,
            "numbercall": -1,
            "interval_number": 1,
            "interval_type": "days",
            "nextcall": now + timedelta(days=1),
            "active": True,
        }

    def _prepare_rule(self):
        self.ensure_one()
        return {
            "name": _("Access %s") % self.name,
            "model_id": self.model_id.id,
            "domain_force": self.domain_force,
            "global": True,
        }

    def _prepare_tree_view(self):
        self.ensure_one()
        return {
            "name": self.name,
            "type": "tree",
            "model": self.model_id.model,
            "arch": """<?xml version="1.0"?>"""
            """<tree string="Analysis">{}"""
            """</tree>""".format(
                "".join([x._prepare_tree_field() for x in self.bi_sql_view_field_ids])
            ),
        }

    def _prepare_graph_view(self):
        self.ensure_one()
        return {
            "name": self.name,
            "type": "graph",
            "model": self.model_id.model,
            "arch": """<?xml version="1.0"?>"""
            """<graph string="Analysis" type="bar" stacked="True">{}"""
            """</graph>""".format(
                "".join([x._prepare_graph_field() for x in self.bi_sql_view_field_ids])
            ),
        }

    def _prepare_pivot_view(self):
        self.ensure_one()
        return {
            "name": self.name,
            "type": "pivot",
            "model": self.model_id.model,
            "arch": """<?xml version="1.0"?>"""
            """<pivot string="Analysis" stacked="True">{}"""
            """</pivot>""".format(
                "".join([x._prepare_pivot_field() for x in self.bi_sql_view_field_ids])
            ),
        }

    def _prepare_search_view(self):
        self.ensure_one()
        return {
            "name": self.name,
            "type": "search",
            "model": self.model_id.model,
            "arch": """<?xml version="1.0"?>"""
            """<search string="Analysis">{}"""
            """<group expand="1" string="Group By">{}</group>"""
            """</search>""".format(
                "".join(
                    [x._prepare_search_field() for x in self.bi_sql_view_field_ids]
                ),
                "".join(
                    [
                        x._prepare_search_filter_field()
                        for x in self.bi_sql_view_field_ids
                    ]
                ),
            ),
        }

    def _prepare_action(self):
        self.ensure_one()
        view_mode = self.view_order
        first_view = view_mode.split(",")[0]
        if first_view == "tree":
            view_id = self.tree_view_id.id
        elif first_view == "pivot":
            view_id = self.pivot_view_id.id
        else:
            view_id = self.graph_view_id.id
        action = safe_eval(self.computed_action_context)
        for k, v in safe_eval(self.action_context).items():
            action[k] = v
        return {
            "name": self._prepare_action_name(),
            "res_model": self.model_id.model,
            "type": "ir.actions.act_window",
            "view_mode": view_mode,
            "view_id": view_id,
            "search_view_id": self.search_view_id.id,
            "context": str(action),
        }

    def _prepare_action_name(self):
        self.ensure_one()
        if not self.is_materialized:
            return self.name
        return "{} ({})".format(
            self.name,
            datetime.utcnow().strftime(_("%m/%d/%Y %H:%M:%S UTC")),
        )

    def _prepare_menu(self):
        self.ensure_one()
        return {
            "name": self.name,
            "parent_id": self.env.ref("bi_sql_editor.menu_bi_sql_editor").id,
            "action": "ir.actions.act_window,%s" % self.action_id.id,
            "sequence": self.sequence,
        }

    # Custom Section
    def _log_execute(self, req):
        _logger.info("Executing SQL Request %s ..." % req)
        self.env.cr.execute(req)

    def _drop_view(self):
        for sql_view in self:
            self._log_execute(
                "DROP %s VIEW IF EXISTS %s"
                % (sql_view.materialized_text, sql_view.view_name)
            )
            sql_view.size = False

    def _create_view(self):
        for sql_view in self:
            sql_view._drop_view()
            try:
                self._log_execute(sql_view._prepare_request_for_execution())
                sql_view._refresh_size()
            except ProgrammingError as e:
                raise UserError(
                    _("SQL Error while creating %s VIEW %s :\n %s")
                    % (sql_view.materialized_text, sql_view.view_name, str(e))
                )

    def _create_index(self):
        for sql_view in self:
            for sql_field in sql_view.bi_sql_view_field_ids.filtered(
                lambda x: x.is_index is True
            ):
                self._log_execute(
                    "CREATE INDEX %s ON %s (%s);"
                    % (sql_field.index_name, sql_view.view_name, sql_field.name)
                )

    def _create_model_and_fields(self):
        for sql_view in self:
            # Create model
            sql_view.model_id = self.env["ir.model"].create(self._prepare_model()).id
            sql_view.rule_id = self.env["ir.rule"].create(self._prepare_rule()).id
            # Drop table, created by the ORM
            if sql.table_exists(self._cr, sql_view.view_name):
                req = "DROP TABLE %s" % sql_view.view_name
                self._log_execute(req)

    def _create_model_access(self):
        for sql_view in self:
            for item in sql_view._prepare_model_access():
                self.env["ir.model.access"].create(item)

    def _drop_model_access(self):
        for sql_view in self:
            self.env["ir.model.access"].search(
                [("model_id", "=", sql_view.model_name)]
            ).unlink()

    def _drop_model_and_fields(self):
        for sql_view in self:
            if sql_view.rule_id:
                sql_view.rule_id.unlink()
            if sql_view.model_id:
                sql_view.model_id.with_context(_force_unlink=True).unlink()

    def _hook_executed_request(self):
        self.ensure_one()
        req = (
            """
            SELECT  attnum,
                    attname AS column,
                    format_type(atttypid, atttypmod) AS type
            FROM    pg_attribute
            WHERE   attrelid = '%s'::regclass
            AND     NOT attisdropped
            AND     attnum > 0
            ORDER   BY attnum;"""
            % self.view_name
        )
        self._log_execute(req)
        return self.env.cr.fetchall()

    def _prepare_request_check_execution(self):
        self.ensure_one()
        return "CREATE VIEW {} AS ({});".format(self.view_name, self.query)

    def _prepare_request_for_execution(self):
        self.ensure_one()
        query = (
            """
            SELECT
                CAST(row_number() OVER () as integer) AS id,
                CAST(Null as timestamp without time zone) as create_date,
                CAST(Null as integer) as create_uid,
                CAST(Null as timestamp without time zone) as write_date,
                CAST(Null as integer) as write_uid,
                my_query.*
            FROM
                (%s) as my_query
        """
            % self.query
        )
        return "CREATE {} VIEW {} AS ({});".format(
            self.materialized_text,
            self.view_name,
            query,
        )

    def _check_execution(self):
        """Ensure that the query is valid, trying to execute it.
        a non materialized view is created for this check.
        A rollback is done at the end.
        After the execution, and before the rollback, an analysis of
        the database structure is done, to know fields type."""
        self.ensure_one()
        sql_view_field_obj = self.env["bi.sql.view.field"]
        columns = super()._check_execution()
        field_ids = []
        for column in columns:
            existing_field = self.bi_sql_view_field_ids.filtered(
                lambda x: x.name == column[1]
            )
            if existing_field:
                # Update existing field
                field_ids.append(existing_field.id)
                existing_field.write({"sequence": column[0], "sql_type": column[2]})
            else:
                # Create a new one if name is prefixed by x_
                if column[1][:2] == "x_":
                    field_ids.append(
                        sql_view_field_obj.create(
                            {
                                "sequence": column[0],
                                "name": column[1],
                                "sql_type": column[2],
                                "bi_sql_view_id": self.id,
                            }
                        ).id
                    )

        # Drop obsolete view field
        self.bi_sql_view_field_ids.filtered(lambda x: x.id not in field_ids).unlink()

        if not self.bi_sql_view_field_ids:
            raise UserError(
                _("No Column was found.\n" "Columns name should be prefixed by 'x_'.")
            )

        return columns

    @api.model
    def _refresh_materialized_view_cron(self, view_ids):
        sql_views = self.search(
            [
                ("is_materialized", "=", True),
                ("state", "in", ["model_valid", "ui_valid"]),
                ("id", "in", view_ids),
            ]
        )
        return sql_views._refresh_materialized_view()

    def _refresh_materialized_view(self):
        for sql_view in self.filtered(lambda x: x.is_materialized):
            req = "REFRESH {} VIEW {}".format(
                sql_view.materialized_text,
                sql_view.view_name,
            )
            self._log_execute(req)
            sql_view._refresh_size()
            if sql_view.action_id:
                # Alter name of the action, to display last refresh
                # datetime of the materialized view
                sql_view.action_id.with_context(
                    lang=self.env.context.get("lang", self.env.user.lang)
                ).name = sql_view._prepare_action_name()

    def _refresh_size(self):
        for sql_view in self:
            req = "SELECT pg_size_pretty(pg_total_relation_size('%s'));" % (
                sql_view.view_name
            )
            self._log_execute(req)
            sql_view.size = self.env.cr.fetchone()[0]

    def check_manual_fields(self, model):
        # check the fields we need are defined on self, to stop it going
        # early on install / startup - particularly problematic during upgrade
        if model._name.startswith(
            self._model_prefix
        ) and "group_operator" in table_columns(self.env.cr, "bi_sql_view_field"):
            # Use SQL instead of ORM, as ORM might not be fully initialised -
            # we have no control over the order that fields are defined!
            # We are not concerned about user security rules.
            self.env.cr.execute(
                """
SELECT
    f.name,
    f.ttype,
    f.group_operator
FROM
    bi_sql_view v
    LEFT JOIN bi_sql_view_field f ON f.bi_sql_view_id = v.id
WHERE
    v.model_name = %s
;
                """,
                (model._name,),
            )
            sql_fields = self.env.cr.fetchall()

            for sql_field in sql_fields:
                if (
                    sql_field[0] in model._fields
                    and sql_field[1] in ("integer", "float")
                    and sql_field[2]
                ):
                    model._fields[sql_field[0]].group_operator = sql_field[2]

    def button_preview_sql_expression(self):
        self.button_validate_sql_expression()
        res = self._execute_sql_request()
        raise UserError("\n".join(map(lambda x: str(x), res[:100])))
