# Copyright 2014 Guewen Baconnier (Camptocamp SA)
# Copyright 2013-2014 Nicolas Bessi (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class BaseCommentTemplate(models.Model):
    _name = "base.comment.template"
    _description = "Base comment template"

    active = fields.Boolean(default=True)

    name = fields.Char(
        string="Comment summary",
        required=True,
    )

    position = fields.Selection(
        selection=[
            ("before_lines", "Before lines"),
            ("after_lines", "After lines"),
        ],
        required=True,
        default="before_lines",
        help="Position on document",
    )

    text = fields.Html(
        string="Comment",
        translate=True,
        required=True,
    )

    company_id = fields.Many2one(
        "res.company",
        string="Company",
        help="If set, it'll only be available for this company",
        ondelete="cascade",
        index=True,
    )

    def get_value(
        self,
        partner_id=False,
        model=None,
        res_id=None,
        engine="jinja",
        add_context=None,
        post_process=False,
    ):
        """Get comment template value.

        Like in mail composer `text` template can use jinja or qweb syntax.

        if `partner_id` is provide, it will retreive it's lang to use the
        right translation.

        Then template is populated with model/res_id attributes according
        jinja/qweb instructions.
        """
        self.ensure_one()
        lang = None
        if partner_id:
            lang = self.env["res.partner"].browse(partner_id).lang
        value = self.with_context(lang=lang).text
        if model is not None and res_id is not None:
            value = self.env["mail.render.mixin"]._render_template(
                value,
                model,
                [res_id],
                engine="jinja",
                add_context=add_context,
                post_process=post_process,
            )[res_id]
        return value
