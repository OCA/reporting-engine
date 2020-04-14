# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class KpiDashboard(models.Model):

    _name = "kpi.dashboard"
    _description = "Dashboard"

    name = fields.Char(required=True)
    active = fields.Boolean(default=True,)
    item_ids = fields.One2many(
        "kpi.dashboard.item", inverse_name="dashboard_id", copy=True,
    )
    number_of_columns = fields.Integer(default=5, required=True)
    width = fields.Integer(compute="_compute_width")
    margin_y = fields.Integer(default=10, required=True)
    margin_x = fields.Integer(default=10, required=True)
    widget_dimension_x = fields.Integer(default=250, required=True)
    widget_dimension_y = fields.Integer(default=250, required=True)
    background_color = fields.Char(required=True, default="#f9f9f9")
    group_ids = fields.Many2many("res.groups",)
    menu_id = fields.Many2one("ir.ui.menu", copy=False)

    def write(self, vals):
        res = super().write(vals)
        if "group_ids" in vals:
            for rec in self:
                if rec.menu_id:
                    rec.menu_id.write(
                        {"groups_id": [(6, 0, rec.group_ids.ids)]}
                    )
        return res

    @api.depends("widget_dimension_x", "margin_x", "number_of_columns")
    def _compute_width(self):
        for rec in self:
            rec.width = (
                rec.margin_x * (rec.number_of_columns + 1)
                + rec.widget_dimension_x * rec.number_of_columns
            )

    def read_dashboard(self):
        self.ensure_one()
        result = {
            "name": self.name,
            "width": self.width,
            "item_ids": self.item_ids.read_dashboard(),
            "max_cols": self.number_of_columns,
            "margin_x": self.margin_x,
            "margin_y": self.margin_y,
            "widget_dimension_x": self.widget_dimension_x,
            "widget_dimension_y": self.widget_dimension_y,
            "background_color": self.background_color,
        }
        if self.menu_id:
            result["action_id"] = self.menu_id.action.id
        return result

    def _generate_menu_vals(self, menu, action):
        return {
            "parent_id": menu.id or False,
            "name": self.name,
            "action": "%s,%s" % (action._name, action.id),
            "groups_id": [(6, 0, self.group_ids.ids)],
        }

    def _generate_action_vals(self, menu):
        return {
            "name": self.name,
            "res_model": self._name,
            "view_mode": "dashboard",
            "res_id": self.id,
        }

    def _generate_menu(self, menu):
        action = self.env["ir.actions.act_window"].create(
            self._generate_action_vals(menu)
        )
        self.menu_id = self.env["ir.ui.menu"].create(
            self._generate_menu_vals(menu, action)
        )


class KpiDashboardItem(models.Model):
    _name = "kpi.dashboard.item"
    _description = "Dashboard Items"
    _order = "row asc, column asc"

    name = fields.Char(required=True)
    kpi_id = fields.Many2one("kpi.kpi")
    dashboard_id = fields.Many2one("kpi.dashboard", required=True,)
    column = fields.Integer(required=True, default=1)
    row = fields.Integer(required=True, default=1)
    end_row = fields.Integer(store=True, compute='_compute_end_row')
    end_column = fields.Integer(store=True, compute='_compute_end_column')
    size_x = fields.Integer(required=True, default=1)
    size_y = fields.Integer(required=True, default=1)
    color = fields.Char()
    font_color = fields.Char()

    @api.depends('row', 'size_y')
    def _compute_end_row(self):
        for r in self:
            r.end_row = r.row + r.size_y - 1

    @api.depends('column', 'size_x')
    def _compute_end_column(self):
        for r in self:
            r.end_column = r.column + r.size_x - 1

    @api.constrains('size_y')
    def _check_size_y(self):
        for rec in self:
            if rec.size_y > 10:
                raise ValidationError(_(
                    'Size Y of the widget cannot be bigger than 10'))

    def _check_size_domain(self):
        return [
            ('dashboard_id', '=', self.dashboard_id.id),
            ('id', '!=', self.id),
            ('row', '<=', self.end_row),
            ('end_row', '>=', self.row),
            ('column', '<=', self.end_column),
            ('end_column', '>=', self.column),
        ]

    @api.constrains('end_row', 'end_column', 'row', 'column')
    def _check_size(self):
        for r in self:
            if self.search(r._check_size_domain(), limit=1):
                raise ValidationError(_(
                    'Widgets cannot be crossed by other widgets'
                ))
            if r.end_column > r.dashboard_id.number_of_columns:
                raise ValidationError(_(
                    'Widget %s is bigger than expected'
                ) % r.display_name)

    @api.onchange("kpi_id")
    def _onchange_kpi(self):
        for rec in self:
            if not rec.name and rec.kpi_id:
                rec.name = rec.kpi_id.name

    def _read_dashboard(self):
        vals = {
            "id": self.id,
            "name": self.name,
            "col": self.column,
            "row": self.row,
            "sizex": self.size_x,
            "sizey": self.size_y,
            "color": self.color,
            "font_color": self.font_color or "000000",
        }
        if self.kpi_id:
            vals.update(
                {
                    "widget": self.kpi_id.widget,
                    "kpi_id": self.kpi_id.id,
                    "suffix": self.kpi_id.suffix or "",
                    "prefix": self.kpi_id.prefix or "",
                    "value": self.kpi_id.value,
                    "value_last_update": self.kpi_id.value_last_update,
                }
            )
            if self.kpi_id.action_ids:
                vals["actions"] = self.kpi_id.action_ids.read_dashboard()
        else:
            vals["widget"] = "base_text"
        return vals

    def read_dashboard(self):
        result = []
        for kpi in self:
            result.append(kpi._read_dashboard())
        return result
