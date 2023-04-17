# Copyright 2014 Guewen Baconnier (Camptocamp SA)
# Copyright 2013-2014 Nicolas Bessi (Camptocamp SA)
# Copyright 2020 NextERP Romania SRL
# Copyright 2021 Tecnativa - Víctor Martínez
# Copyright 2023 Tecnativa - Pedro M. Baeza
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
            domain = [
                "|",
                ("partner_ids", "=", False),
                ("partner_ids", "=", partner.id),
                ("model_ids.model", "=", self._name),
            ]
            if "company_id" in self._fields:
                domain += [
                    "|",
                    ("company_id", "=", False),
                    ("company_id", "=", record.company_id.id),
                ]
            templates = self.env["base.comment.template"].search(domain)
            for template in templates:
                domain = safe_eval(template.domain)
                if not domain or record.filtered_domain(domain):
                    record.comment_template_ids = [(4, template.id)]
            if not templates:
                record.comment_template_ids = False

    def render_comment(
        self, comment, engine="jinja", add_context=None, post_process=False
    ):
        self.ensure_one()
        comment_texts = self.env["mail.render.mixin"]._render_template(
            comment.text,
            self._name,
            [self.id],
            engine=engine,
            add_context=add_context,
            post_process=post_process,
        )
        return comment_texts[self.id] or ""
