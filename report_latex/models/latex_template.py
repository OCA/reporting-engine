# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class LatexTemplate(models.Model):
    _name = "latex.template"
    _description = "Latex template"
    _inherit = "mail.thread"

    name = fields.Char(required=True)
    file_name = fields.Char(compute="_compute_file_name")

    is_root = fields.Boolean(default=False)
    subtemplate_ids = fields.Many2many(
        comodel_name="latex.template",
        relation="latex_template_subtemplate_rel",
        column1="template_id",
        column2="subtemplate_id",
        string="Input Templates",
        domain="[('is_root', '=', False)]",
    )
    attachment_ids = fields.Many2many(
        comodel_name="ir.attachment", string="Attachments"
    )
    content = fields.Text(required=True)

    @api.depends("name")
    def _compute_file_name(self):
        for record in self:
            if record.name:
                # Clean filename and add .tex extension
                safe_name = "".join(
                    c for c in record.name if c.isalnum() or c in (" ", "-", "_")
                ).rstrip()
                safe_name = safe_name.replace(" ", "_")
                record.file_name = f"{safe_name}.tex"
            else:
                record.file_name = "template.tex"
