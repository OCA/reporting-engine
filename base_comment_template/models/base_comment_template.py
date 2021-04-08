# Copyright 2014 Guewen Baconnier (Camptocamp SA)
# Copyright 2013-2014 Nicolas Bessi (Camptocamp SA)
# Copyright 2020 NextERP Romania SRL
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class CommentTemplate(models.AbstractModel):
    _name = "comment.template"
    _description = (
        "base.comment.template to put header and footer "
        "in reports based on created comment templates"
    )

    def get_comment_template_records(
        self, position="before_lines", company_id=False, partner_id=False
    ):
        self.ensure_one()
        if not company_id:
            company_id = self.env.company.id
        present_model_id = self.env["ir.model"].search([("model", "=", self._name)])
        default_dom = [
            ("model_ids", "in", present_model_id.id),
            ("position", "=", position),
        ]
        lang = False
        if partner_id and "partner_id" in self._fields:
            default_dom += [
                "|",
                ("partner_ids", "=", False),
                ("partner_ids", "in", partner_id),
            ]
            lang = self.env["res.partner"].browse(partner_id).lang
        if company_id and "company_id" in self._fields:
            if partner_id and "partner_id" in self._fields:
                default_dom.insert(-3, "&")
            default_dom += [
                "|",
                ("company_id", "=", company_id),
                ("company_id", "=", False),
            ]
        templates = self.env["base.comment.template"].search(
            default_dom, order="priority"
        )
        if lang:
            templates = templates.with_context({"lang": lang})
        return templates

    def get_comment_template(
        self, position="before_lines", company_id=False, partner_id=False
    ):
        """ Method that is called from report xml and is returning the
            position template as a html if exists
        """
        self.ensure_one()
        templates = self.get_comment_template_records(
            position=position, company_id=company_id, partner_id=partner_id
        )
        template = False
        if templates:
            for templ in templates:
                if self in self.search(safe_eval(templ.domain or "[]")):
                    template = templ
                    break
        if not template:
            return ""
        return self.env["mail.template"]._render_template(
            template.text, self._name, self.id, post_process=True
        )


class BaseCommentTemplate(models.Model):
    """Comment templates printed on reports"""

    _name = "base.comment.template"
    _description = "Comments Template"

    active = fields.Boolean(default=True)
    position = fields.Selection(
        string="Position on document",
        selection=[("before_lines", "Before lines"), ("after_lines", "After lines")],
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
        "res.company",
        string="Company",
        ondelete="cascade",
        index=True,
        help="If set, the comment template will be available only for the selected "
        "company.",
    )
    partner_ids = fields.Many2many(
        comodel_name="res.partner",
        string="Partner",
        ondelete="cascade",
        help="If set, the comment template will be available only for the selected "
        "partner.",
    )

    model_ids = fields.Many2many(
        comodel_name="ir.model",
        string="IR Model",
        ondelete="cascade",
        required=True,
        help="This comment template will be available on this models. "
        "You can see here only models allowed to set the coment template.",
    )

    domain = fields.Char(
        "Filter Domain",
        required=True,
        default="[]",
        help="This comment template will be available only for objects "
        "that satisfy the condition",
    )

    priority = fields.Integer(
        default=10, copy=False, help="the highest priority = the smallest number",
    )

    @api.constrains("domain", "priority", "model_ids", "position")
    def _check_partners_in_company_id(self):
        templates = self.search([])
        for record in self:
            other_template_same_models_and_priority = templates.filtered(
                lambda t: t.priority == record.priority
                and set(record.model_ids).intersection(record.model_ids)
                and t.domain == record.domain
                and t.position == record.position
                and t.id != record.id
            )
            if other_template_same_models_and_priority:
                raise ValidationError(
                    _(
                        "There are other records with same models, priority, "
                        "domain and position."
                    )
                )

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        # modify the form view of base_commnent_template
        # Add domain on model_id to get only models that have a report set
        # and those whom have inherited this model
        res = super().fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )
        if view_type == "form":
            doc = etree.XML(res["arch"])
            for node in doc.xpath("//field[@name='model_ids']"):
                report_models = self.env["ir.actions.report"].search([]).mapped("model")
                model_ids = (
                    self.env["ir.model"]
                    .search(
                        [
                            ("model", "in", report_models),
                            ("is_comment_template", "=", True),
                            "!",
                            ("name", "=like", "ir.%"),
                        ]
                    )
                    .ids
                )
                model_filter = "[('id','in'," + str(model_ids) + ")]"
                node.set("domain", model_filter)
            res["arch"] = etree.tostring(doc, encoding="unicode")
        return res
