# Copyright 2014 Guewen Baconnier (Camptocamp SA)
# Copyright 2013-2014 Nicolas Bessi (Camptocamp SA)
# Copyright 2020 NextERP Romania SRL
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import fields, models


class BaseCommentTemplate(models.Model):
    """Comment templates printed on reports"""

    _name = "base.comment.template"
    _description = "Comments Template"
    _order = "sequence,id"

    active = fields.Boolean(default=True)
    position = fields.Selection(
        string="Position on document",
        selection=[("before_lines", "Top"), ("after_lines", "Bottom")],
        required=True,
        default="before_lines",
        help="This field allows to select the position of the comment on reports.",
    )
    name = fields.Char(
        string="Name",
        translate=True,
        required=True,
        help="Name/description of this comment template",
    )
    text = fields.Html(
        string="Template",
        translate=True,
        required=True,
        sanitize=False,
        help="This is the text template that will be inserted into reports.",
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        string="Company",
        ondelete="cascade",
        index=True,
        help="If set, the comment template will be available only for the selected "
        "company.",
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="base_comment_template_res_partner_rel",
        column1="base_comment_template_id",
        column2="res_partner_id",
        string="Partner",
        readonly=True,
        help="If set, the comment template will be available only for the selected "
        "partner.",
    )
    model_ids = fields.Many2many(
        comodel_name="ir.model",
        string="IR Model",
        ondelete="cascade",
        domain=[
            ("is_comment_template", "=", True),
            ("model", "!=", "comment.template"),
        ],
        required=True,
        help="This comment template will be available on this models. "
        "You can see here only models allowed to set the coment template.",
    )
    domain = fields.Char(
        string="Filter Domain",
        required=True,
        default="[]",
        help="This comment template will be available only for objects "
        "that satisfy the condition",
    )
    sequence = fields.Integer(
        required=True, default=10, help="The smaller number = The higher priority"
    )

    def name_get(self):
        """Redefine the name_get method to show the template name with the position."""
        res = []
        for item in self:
            name = "{} ({})".format(
                item.name, dict(self._fields["position"].selection).get(item.position)
            )
            if self.env.context.get("comment_template_model_display"):
                name += " (%s)" % ", ".join(item.model_ids.mapped("name"))
            res.append((item.id, name))
        return res
