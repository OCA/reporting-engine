from odoo import api, fields, models
from odoo.tools.safe_eval import safe_eval

from odoo.addons.base.models.res_partner import _lang_get


class BaseCommentTemplatePreview(models.TransientModel):
    _name = "base.comment.template.preview"
    _description = "Base Comment Template Preview"

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search([("is_comment_template", "=", True)])
        return [(model.model, model.name) for model in models]

    @api.model
    def default_get(self, fields):
        result = super().default_get(fields)
        base_comment_template_id = self.env.context.get(
            "default_base_comment_template_id"
        )
        if not base_comment_template_id or "resource_ref" not in fields:
            return result
        base_comment_template = self.env["base.comment.template"].browse(
            base_comment_template_id
        )
        result["model_ids"] = base_comment_template.model_ids
        domain = safe_eval(base_comment_template.domain)
        model = (
            base_comment_template.model_ids[0]
            if base_comment_template.model_ids
            else False
        )
        res = self.env[model.model].search(domain, limit=1)
        if res:
            result["resource_ref"] = "%s,%s" % (model.model, res.id)
        return result

    base_comment_template_id = fields.Many2one(
        "base.comment.template", required=True, ondelete="cascade"
    )
    lang = fields.Selection(_lang_get, string="Template Preview Language")
    engine = fields.Selection(
        [
            ("inline_template", "Inline template"),
            ("qweb", "QWeb"),
            ("qweb_view", "QWeb view"),
        ],
        string="Template Preview Engine",
        default="inline_template",
    )
    model_ids = fields.Many2many(
        "ir.model", related="base_comment_template_id.model_ids"
    )
    model_id = fields.Many2one("ir.model")
    body = fields.Char(compute="_compute_base_comment_template_fields")
    resource_ref = fields.Reference(
        string="Record reference", selection="_selection_target_model"
    )
    no_record = fields.Boolean(compute="_compute_no_record")

    @api.depends("model_id")
    def _compute_no_record(self):
        for preview in self:
            domain = safe_eval(self.base_comment_template_id.domain)
            preview.no_record = (
                (self.env[preview.model_id.model].search_count(domain) == 0)
                if preview.model_id
                else True
            )

    @api.depends("lang", "resource_ref", "engine")
    def _compute_base_comment_template_fields(self):
        for wizard in self:
            if (
                wizard.model_id
                and wizard.resource_ref
                and wizard.lang
                and wizard.engine
            ):
                wizard.body = wizard.resource_ref.with_context(
                    lang=wizard.lang
                ).render_comment(self.base_comment_template_id, engine=wizard.engine)
            else:
                wizard.body = wizard.base_comment_template_id.text
