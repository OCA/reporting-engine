# Copyright 2015-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import json

import pydot
from psycopg2.extensions import AsIs

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError


class BveView(models.Model):
    _name = "bve.view"
    _description = "BI View Editor"

    @api.depends("group_ids", "group_ids.users")
    def _compute_users(self):
        for bve_view in self.sudo():
            if bve_view.group_ids:
                bve_view.user_ids = bve_view.group_ids.mapped("users")
            else:
                bve_view.user_ids = self.env["res.users"].sudo().search([])

    @api.depends("name")
    def _compute_model_name(self):
        for bve_view in self:
            name = [x for x in bve_view.name.lower() if x.isalnum()]
            model_name = "".join(name).replace("_", ".").replace(" ", ".")
            bve_view.model_name = "x_bve." + model_name

    def _compute_serialized_data(self):
        for bve_view in self:
            serialized_data = []
            for line in bve_view.line_ids.sorted(key=lambda r: r.sequence):
                serialized_data.append(
                    {
                        "sequence": line.sequence,
                        "model_id": line.model_id.id,
                        "id": line.field_id.id,
                        "name": line.name,
                        "model_name": line.model_id.name,
                        "model": line.model_id.model,
                        "type": line.ttype,
                        "table_alias": line.table_alias,
                        "description": line.description,
                        "row": line.row,
                        "column": line.column,
                        "measure": line.measure,
                        "list": line.in_list,
                        "join_node": line.join_node,
                        "relation": line.relation,
                    }
                )
            bve_view.data = json.dumps(serialized_data)

    def _inverse_serialized_data(self):
        for bve_view in self:
            line_ids = self._sync_lines_and_data(bve_view.data)
            bve_view.write({"line_ids": line_ids})

    name = fields.Char(required=True, copy=False, default="")
    model_name = fields.Char(compute="_compute_model_name", store=True)
    note = fields.Text(string="Notes")
    state = fields.Selection(
        [("draft", "Draft"), ("created", "Created")], default="draft", copy=False
    )
    data = fields.Char(
        compute="_compute_serialized_data",
        inverse="_inverse_serialized_data",
        help="Use the special query builder to define the query "
        "to generate your report dataset. "
        "NOTE: To be edited, the query should be in 'Draft' status.",
    )
    line_ids = fields.One2many("bve.view.line", "bve_view_id", string="Lines")
    field_ids = fields.One2many(
        "bve.view.line",
        "bve_view_id",
        domain=["|", ("join_node", "=", -1), ("join_node", "=", False)],
        string="Fields",
    )
    relation_ids = fields.One2many(
        "bve.view.line",
        "bve_view_id",
        domain=[("join_node", "!=", -1), ("join_node", "!=", False)],
        string="Relations",
    )
    action_id = fields.Many2one("ir.actions.act_window", string="Action")
    view_id = fields.Many2one("ir.ui.view", string="View")
    group_ids = fields.Many2many(
        "res.groups",
        string="Groups",
        help="User groups allowed to see the generated report; "
        "if NO groups are specified the report will be public "
        "for everyone.",
    )
    user_ids = fields.Many2many(
        "res.users", string="Users", compute="_compute_users", store=True
    )
    query = fields.Text(compute="_compute_sql_query")
    over_condition = fields.Text(
        states={"draft": [("readonly", False)]},
        readonly=True,
        help="Condition to be inserted in the OVER part "
        "of the ID's row_number function.\n"
        "For instance, 'ORDER BY t1.id' would create "
        "IDs ordered in the same way as t1's IDs; otherwise "
        "IDs are assigned with no specific order.",
    )
    er_diagram_image = fields.Binary(compute="_compute_er_diagram_image")

    _sql_constraints = [
        ("name_uniq", "unique(name)", _("Custom BI View names must be unique!")),
    ]

    @api.depends("line_ids")
    def _compute_er_diagram_image(self):
        for bve_view in self:
            graph = pydot.Dot(graph_type="graph")
            table_model_map = {}
            for line in bve_view.field_ids:
                if line.table_alias not in table_model_map:
                    table_alias_node = pydot.Node(
                        line.model_id.name + " " + line.table_alias,
                        style="filled",
                        shape="box",
                        fillcolor="#DDDDDD",
                    )
                    table_model_map[line.table_alias] = table_alias_node
                    graph.add_node(table_model_map[line.table_alias])
                field_node = pydot.Node(
                    line.table_alias + "." + line.field_id.field_description,
                    label=line.description,
                    style="filled",
                    fillcolor="green",
                )
                graph.add_node(field_node)
                graph.add_edge(
                    pydot.Edge(table_model_map[line.table_alias], field_node)
                )
            for line in bve_view.relation_ids:
                field_description = line.field_id.field_description
                table_alias = line.table_alias
                diamond_node = pydot.Node(
                    line.ttype + " " + table_alias + "." + field_description,
                    label=table_alias + "." + field_description,
                    style="filled",
                    shape="diamond",
                    fillcolor="#D2D2FF",
                )
                graph.add_node(diamond_node)
                graph.add_edge(
                    pydot.Edge(
                        table_model_map[table_alias],
                        diamond_node,
                        labelfontcolor="#D2D2FF",
                        color="blue",
                    )
                )
                graph.add_edge(
                    pydot.Edge(
                        diamond_node,
                        table_model_map[line.join_node],
                        labelfontcolor="black",
                        color="blue",
                    )
                )
            try:
                png_base64_image = base64.b64encode(graph.create_png())
                bve_view.er_diagram_image = png_base64_image
            except Exception:
                bve_view.er_diagram_image = False

    def _create_view_arch(self):
        self.ensure_one()

        def _get_field_def(line):
            field_type = line.view_field_type
            return '<field name="{}" type="{}" />'.format(line.name, field_type)

        bve_field_lines = self.field_ids.filtered("view_field_type")
        return list(map(_get_field_def, bve_field_lines))

    def _create_tree_view_arch(self):
        self.ensure_one()

        def _get_field_attrs(line):
            attr = line.list_attr
            res = attr and '{}="{}"'.format(attr, line.description) or ""
            return '<field name="{}" {} />'.format(line.name, res)

        bve_field_lines = self.field_ids.filtered(lambda l: l.in_list)
        return list(map(_get_field_attrs, bve_field_lines.sorted("sequence")))

    def _create_bve_view(self):
        self.ensure_one()
        View = self.env["ir.ui.view"].sudo()

        # delete old views
        View.search([("model", "=", self.model_name)]).unlink()

        # create views
        View.create(
            [
                {
                    "name": "Pivot Analysis",
                    "type": "pivot",
                    "model": self.model_name,
                    "priority": 16,
                    "arch": """<?xml version="1.0"?>
                       <pivot string="Pivot Analysis">
                       {}
                       </pivot>
                    """.format(
                        "".join(self._create_view_arch())
                    ),
                },
                {
                    "name": "Graph Analysis",
                    "type": "graph",
                    "model": self.model_name,
                    "priority": 16,
                    "arch": """<?xml version="1.0"?>
                       <graph string="Graph Analysis"
                        type="bar" stacked="True">
                        {}
                       </graph>
                    """.format(
                        "".join(self._create_view_arch())
                    ),
                },
                {
                    "name": "Search BI View",
                    "type": "search",
                    "model": self.model_name,
                    "priority": 16,
                    "arch": """<?xml version="1.0"?>
                       <search>
                       {}
                       </search>
                    """.format(
                        "".join(self._create_view_arch())
                    ),
                },
            ]
        )

        # create Tree view
        tree_view = View.create(
            {
                "name": "Tree Analysis",
                "type": "tree",
                "model": self.model_name,
                "priority": 16,
                "arch": """<?xml version="1.0"?>
                       <tree create="false">
                       {}
                       </tree>
                    """.format(
                    "".join(self._create_tree_view_arch())
                ),
            }
        )

        # set the Tree view as the default one
        action = (
            self.env["ir.actions.act_window"]
            .sudo()
            .create(
                {
                    "name": self.name,
                    "res_model": self.model_name,
                    "type": "ir.actions.act_window",
                    "view_mode": "tree,graph,pivot",
                    "view_id": tree_view.id,
                    "context": "{'service_name': '%s'}" % self.name,
                }
            )
        )

        self.write(
            {"action_id": action.id, "view_id": tree_view.id, "state": "created"}
        )

    def _build_access_rules(self, model):
        self.ensure_one()

        if not self.group_ids:
            self.env["ir.model.access"].sudo().create(
                {
                    "name": "read access to " + self.model_name,
                    "model_id": model.id,
                    "perm_read": True,
                }
            )
        else:
            # read access only to model
            access_vals = [
                {
                    "name": "read access to " + self.model_name,
                    "model_id": model.id,
                    "group_id": group.id,
                    "perm_read": True,
                }
                for group in self.group_ids
            ]
            self.env["ir.model.access"].sudo().create(access_vals)

    def _create_sql_view(self):
        self.ensure_one()

        view_name = self.model_name.replace(".", "_")
        query = self.query and self.query.replace("\n", " ")

        # robustness in case something went wrong
        self._cr.execute("DROP TABLE IF EXISTS %s", (AsIs(view_name),))

        # create postgres view
        try:
            with self.env.cr.savepoint():
                self.env.cr.execute(
                    "CREATE or REPLACE VIEW %s as (%s)",
                    (
                        AsIs(view_name),
                        AsIs(query),
                    ),
                )
        except Exception as e:
            raise UserError(
                _("Error creating the view '{query}':\n{error}").format(
                    query=query, error=e
                )
            )

    @api.depends("line_ids", "state", "over_condition")
    def _compute_sql_query(self):
        for bve_view in self:
            tables_map = {}
            select_str = "\n CAST(row_number() OVER ({}) as integer) AS id".format(
                bve_view.over_condition or ""
            )
            for line in bve_view.field_ids:
                table = line.table_alias
                select = line.field_id.name
                as_name = line.name
                select_str += ",\n {}.{} AS {}".format(table, select, as_name)

                if line.table_alias not in tables_map:
                    table = self.env[line.field_id.model_id.model]._table
                    tables_map[line.table_alias] = table
            seen = set()
            from_str = ""
            if not bve_view.relation_ids and bve_view.field_ids:
                first_line = bve_view.field_ids[0]
                table = tables_map[first_line.table_alias]
                from_str = "{} AS {}".format(table, first_line.table_alias)
            for line in bve_view.relation_ids:
                table = tables_map[line.table_alias]
                table_format = "{} AS {}".format(table, line.table_alias)
                if not from_str:
                    from_str += table_format
                    seen.add(line.table_alias)
                if line.table_alias not in seen:
                    seen.add(line.table_alias)
                    from_str += "\n"
                    from_str += " LEFT" if line.left_join else ""
                    from_str += " JOIN {} ON {}.id = {}.{}".format(
                        table_format,
                        line.join_node,
                        line.table_alias,
                        line.field_id.name,
                    )
                if line.join_node not in seen:
                    from_str += "\n"
                    seen.add(line.join_node)
                    from_str += " LEFT" if line.left_join else ""
                    from_str += " JOIN {} AS {} ON {}.{} = {}.id".format(
                        tables_map[line.join_node],
                        line.join_node,
                        line.table_alias,
                        line.field_id.name,
                        line.join_node,
                    )
            bve_view.query = """SELECT %s\n\nFROM %s
                """ % (
                AsIs(select_str),
                AsIs(from_str),
            )

    def action_translations(self):
        self.ensure_one()
        if self.state != "created":
            return
        self = self.sudo()
        model = self.env["ir.model"].search([("model", "=", self.model_name)])
        IrTranslation = self.env["ir.translation"]
        IrTranslation.translate_fields("ir.model", model.id)
        for field in model.field_id:
            IrTranslation.translate_fields("ir.model.fields", field.id)
        return {
            "name": "Translations",
            "res_model": "ir.translation",
            "type": "ir.actions.act_window",
            "view_mode": "tree",
            "view_id": self.env.ref("base.view_translation_dialog_tree").id,
            "target": "current",
            "flags": {"search_view": True, "action_buttons": True},
            "domain": [
                "|",
                "&",
                ("res_id", "in", model.field_id.ids),
                ("name", "=", "ir.model.fields,field_description"),
                "&",
                ("res_id", "=", model.id),
                ("name", "=", "ir.model,name"),
            ],
        }

    def action_create(self):
        self.ensure_one()

        # consistency checks
        self._check_invalid_lines()
        self._check_groups_consistency()

        # force removal of dirty views in case something went wrong
        self.sudo().action_reset()

        # create sql view
        self._create_sql_view()

        # create model and fields
        bve_fields = self.line_ids.filtered(lambda l: not l.join_node)
        model = (
            self.env["ir.model"]
            .sudo()
            .with_context(bve=True)
            .create(
                {
                    "name": self.name,
                    "model": self.model_name,
                    "state": "manual",
                    "field_id": [(0, 0, f) for f in bve_fields._prepare_field_vals()],
                }
            )
        )

        # give access rights
        self._build_access_rules(model)

        # create tree, graph and pivot views
        self._create_bve_view()

    def _check_groups_consistency(self):
        self.ensure_one()

        if not self.group_ids:
            return

        for line_model in self.line_ids.mapped("model_id"):
            res_count = (
                self.env["ir.model.access"]
                .sudo()
                .search(
                    [
                        ("model_id", "=", line_model.id),
                        ("perm_read", "=", True),
                        "|",
                        ("group_id", "=", False),
                        ("group_id", "in", self.group_ids.ids),
                    ],
                    limit=1,
                )
            )
            if not res_count:
                access_records = (
                    self.env["ir.model.access"]
                    .sudo()
                    .search(
                        [("model_id", "=", line_model.id), ("perm_read", "=", True)]
                    )
                )
                group_list = ""
                for group in access_records.mapped("group_id"):
                    group_list += " * {}\n".format(group.full_name)
                msg_title = _(
                    'The model "%s" cannot be accessed by users with the '
                    "selected groups only." % (line_model.name,)
                )
                msg_details = _("At least one of the following groups must be added:")
                raise UserError(
                    _("{}\n\n{}\n{}".format(msg_title, msg_details, group_list))
                )

    def _check_invalid_lines(self):
        self.ensure_one()
        if not self.line_ids:
            raise ValidationError(_("No data to process."))

        invalid_lines = self.line_ids.filtered(lambda l: not l.model_id)
        if invalid_lines:
            missing_models = ", ".join(set(invalid_lines.mapped("model_name")))
            raise ValidationError(
                _(
                    "Following models are missing: %s.\n"
                    "Probably some modules were uninstalled." % (missing_models,)
                )
            )
        invalid_lines = self.line_ids.filtered(lambda l: not l.field_id)
        if invalid_lines:
            missing_fields = ", ".join(set(invalid_lines.mapped("field_name")))
            raise ValidationError(
                _("Following fields are missing: {}.".format(missing_fields))
            )

    def open_view(self):
        self.ensure_one()
        self._check_invalid_lines()
        [action] = self.action_id.read()
        action["display_name"] = _("BI View")
        return action

    def copy(self, default=None):
        self.ensure_one()
        default = dict(default or {}, name=_("%s (copy)") % self.name)
        return super().copy(default=default)

    def action_reset(self):
        self.ensure_one()

        has_menus = False
        if self.action_id:
            action = "ir.actions.act_window,%d" % (self.action_id.id,)
            menus = self.env["ir.ui.menu"].search([("action", "=", action)])
            has_menus = True if menus else False
            menus.unlink()

            if self.action_id.view_id:
                self.sudo().action_id.view_id.unlink()
            self.sudo().action_id.unlink()

        self.env["ir.ui.view"].sudo().search([("model", "=", self.model_name)]).unlink()
        models_to_delete = (
            self.env["ir.model"].sudo().search([("model", "=", self.model_name)])
        )
        if models_to_delete:
            models_to_delete.with_context(_force_unlink=True).unlink()

        table_name = self.model_name.replace(".", "_")
        tools.drop_view_if_exists(self.env.cr, table_name)

        self.state = "draft"

        if has_menus:
            return {"type": "ir.actions.client", "tag": "reload"}

    def unlink(self):
        if self.filtered(lambda v: v.state == "created"):
            raise UserError(
                _("You cannot delete a created view! " "Reset the view to draft first.")
            )
        return super().unlink()

    @api.model
    def _sync_lines_and_data(self, data):
        line_ids = [(5, 0, 0)]
        fields_info = []
        if data:
            fields_info = json.loads(data)

        table_model_map = {}
        for item in fields_info:
            if item.get("join_node", -1) == -1:
                table_model_map[item["table_alias"]] = item["model_id"]

        for sequence, field_info in enumerate(fields_info, start=1):
            join_model_id = False
            join_node = field_info.get("join_node", -1)
            if join_node != -1 and table_model_map.get(join_node):
                join_model_id = int(table_model_map[join_node])

            line_ids += [
                (
                    0,
                    False,
                    {
                        "sequence": sequence,
                        "model_id": field_info["model_id"],
                        "table_alias": field_info["table_alias"],
                        "description": field_info["description"],
                        "field_id": field_info["id"],
                        "ttype": field_info["type"],
                        "row": field_info["row"],
                        "column": field_info["column"],
                        "measure": field_info["measure"],
                        "in_list": field_info["list"],
                        "relation": field_info.get("relation"),
                        "join_node": field_info.get("join_node"),
                        "join_model_id": join_model_id,
                    },
                )
            ]
        return line_ids

    @api.constrains("line_ids")
    def _constraint_line_ids(self):
        models_with_tables = self.env.registry.models.keys()
        for view in self:
            nodes = view.line_ids.filtered(lambda n: n.join_node)
            nodes_models = nodes.mapped("table_alias")
            nodes_models += nodes.mapped("join_node")
            not_nodes = view.line_ids.filtered(lambda n: not n.join_node)
            not_nodes_models = not_nodes.mapped("table_alias")
            err_msg = _("Inconsistent lines.")
            if set(nodes_models) - set(not_nodes_models):
                raise ValidationError(err_msg)
            if len(set(not_nodes_models) - set(nodes_models)) > 1:
                raise ValidationError(err_msg)
            models = view.line_ids.mapped("model_id")
            if models.filtered(lambda m: m.model not in models_with_tables):
                raise ValidationError(_("Abstract models not supported."))

    @api.model
    def get_clean_list(self, data_dict):
        serialized_data = data_dict
        if type(data_dict) == str:
            serialized_data = json.loads(data_dict)
        table_alias_list = set()
        for item in serialized_data:
            if item.get("join_node", -1) in [-1, False]:
                table_alias_list.add(item["table_alias"])

        for item in serialized_data:
            if item.get("join_node", -1) not in [-1, False]:
                if item["table_alias"] not in table_alias_list:
                    serialized_data.remove(item)
                elif item["join_node"] not in table_alias_list:
                    serialized_data.remove(item)

        return json.dumps(serialized_data)
