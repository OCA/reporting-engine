# Copyright 2014 Guewen Baconnier (Camptocamp SA)
# Copyright 2013-2014 Nicolas Bessi (Camptocamp SA)
# Copyright 2020 NextERP Romania SRL
# Copyright 2021-2022 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models
from odoo.osv import expression
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
        compute_sudo=True,
        comodel_name="base.comment.template",
        string="Comment Template",
        domain=lambda self: [("model_ids", "in", self._name)],
        store=True,
        readonly=False,
    )

    @api.depends(_comment_template_partner_field_name)
    def _compute_comment_template_ids(self):
        template_model = self.env["base.comment.template"]
        template_domain = template_model._search_model_ids("in", self._name)
        for record in self:
            partner = record[self._comment_template_partner_field_name]
            record.comment_template_ids = [(5,)]
            templates = template_model.search(
                expression.AND(
                    [
                        [("id", "in", partner.base_comment_template_ids.ids)],
                        template_domain,
                    ]
                )
            )
            for template in templates:
                domain = safe_eval(template.domain)
                if not domain or record.filtered_domain(domain):
                    record.comment_template_ids = [(4, template.id)]

    def render_comment(
        self, comment, engine="inline_template", add_context=None, post_process=False
    ):
        self.ensure_one()
        comment_texts = self.env["mail.render.mixin"]._render_template(
            template_src=comment.text,
            model=self._name,
            res_ids=[self.id],
            engine=engine,
            add_context=add_context,
            post_process=post_process,
        )
        return comment_texts[self.id] or ""
