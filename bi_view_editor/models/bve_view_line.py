# Copyright 2015-2020 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class BveViewLine(models.Model):
    _name = "bve.view.line"
    _description = "BI View Editor Lines"

    name = fields.Char(compute="_compute_name")
    sequence = fields.Integer(default=1)
    bve_view_id = fields.Many2one("bve.view", ondelete="cascade")
    model_id = fields.Many2one("ir.model")
    model_name = fields.Char(related="model_id.model", store=True, string="Model Name")
    table_alias = fields.Char(required=True)
    join_model_id = fields.Many2one("ir.model")
    field_id = fields.Many2one("ir.model.fields")
    field_name = fields.Char(compute="_compute_model_field_name", store=True)
    ttype = fields.Char(string="Type")
    description = fields.Char(translate=True)
    relation = fields.Char()
    join_node = fields.Char()
    left_join = fields.Boolean()

    row = fields.Boolean()
    column = fields.Boolean()
    measure = fields.Boolean()
    in_list = fields.Boolean()
    list_attr = fields.Selection(
        [("sum", "Sum"), ("avg", "Average")], string="List Attribute", default="sum"
    )
    view_field_type = fields.Char(compute="_compute_view_field_type")

    @api.depends("row", "column", "measure")
    def _compute_view_field_type(self):
        for line in self:
            row = line.row and "row"
            column = line.column and "col"
            measure = line.measure and "measure"
            line.view_field_type = row or column or measure

    @api.constrains("row", "column", "measure")
    def _constrains_options_check(self):
        measure_types = ["float", "integer", "monetary"]
        for line in self.filtered(lambda l: l.row or l.column):
            if line.join_model_id or line.ttype in measure_types:
                err_msg = _("This field cannot be a row or a column.")
                raise ValidationError(err_msg)
        for line in self.filtered(lambda l: l.measure):
            if line.join_model_id or line.ttype not in measure_types:
                err_msg = _("This field cannot be a measure.")
                raise ValidationError(err_msg)

    @api.constrains("table_alias", "field_id")
    def _constrains_unique_fields_check(self):
        seen = set()
        for line in self.mapped("bve_view_id.field_ids"):
            if (
                line.table_alias,
                line.field_id.id,
            ) not in seen:
                seen.add(
                    (
                        line.table_alias,
                        line.field_id.id,
                    )
                )
            else:
                raise ValidationError(
                    _("Field %s/%s is duplicated.\n" "Please remove the duplications.")
                    % (line.field_id.model, line.field_id.name)
                )

    @api.depends("field_id", "sequence")
    def _compute_name(self):
        for line in self:
            line.name = False
            if line.field_id:
                line.name = "x_bve_{}_{}".format(line.table_alias, line.field_id.name)

    @api.depends("field_id")
    def _compute_model_field_name(self):
        for line in self:
            line.field_name = False
            if line.field_id:
                line.field_name = "{} ({})".format(line.description, line.model_name)

    def _prepare_field_vals(self):
        vals_list = []
        for line in self:
            field = line.field_id
            vals = {
                "name": line.name,
                "complete_name": field.complete_name,
                "model": line.bve_view_id.model_name,
                "relation": field.relation,
                "field_description": line.description,
                "ttype": field.ttype,
                "selection": field.selection,
                "size": field.size,
                "state": "manual",
                "readonly": True,
                "groups": [(6, 0, field.groups.ids)],
            }
            if vals["ttype"] == "monetary":
                vals.update({"ttype": "float"})
            if field.ttype == "selection" and not field.selection:
                model_obj = self.env[field.model_id.model]
                selection = model_obj._fields[field.name].selection
                if callable(selection):
                    selection_domain = selection(model_obj)
                else:
                    selection_domain = selection
                vals.update({"selection": str(selection_domain)})
            vals_list.append(vals)
        return vals_list
