# Copyright 2014 Guewen Baconnier (Camptocamp SA)
# Copyright 2013-2014 Nicolas Bessi (Camptocamp SA)
# Copyright 2020 NextERP Romania SRL
# Copyright 2021 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval


class CommentTemplate(models.AbstractModel):
    _name = "comment.template"
    _description = (
        "base.comment.template to put header and footer "
        "in reports based on created comment templates"
    )
    # This field allows to set any given field that determines the source partner for
    # the comment templates downstream.
    # E.g.: other models where the partner field is called customer_id.
    _comment_template_partner_field_name = "partner_id"

    comment_template_ids = fields.Many2many(
        compute="_compute_comment_template_ids",
        comodel_name="base.comment.template",
        string="Comment Template",
        domain=lambda self: [("model_ids.model", "=", self._name)],
        store=True,
        readonly=False,
    )

    @api.depends(_comment_template_partner_field_name)
    def _compute_comment_template_ids(self):
        for record in self:
            partner = record[self._comment_template_partner_field_name]
            record.comment_template_ids = [(5,)]
            templates = self.env["base.comment.template"].search(
                [
                    ("id", "in", partner.base_comment_template_ids.ids),
                    ("model_ids.model", "=", self._name),
                ]
            )
            for template in templates:
                domain = safe_eval(template.domain)
                if not domain or record.filtered_domain(domain):
                    record.comment_template_ids = [(4, template.id)]
