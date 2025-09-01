# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
import subprocess
import tempfile
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval, time

logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("latex", "latex")],
        ondelete={"latex": "cascade"},
    )
    latex_template_id = fields.Many2one(
        comodel_name="latex.template",
        string="Latex template",
        domain="[('is_root', '=', True)]",
    )

    @api.constrains("latex_template_id", "report_type")
    def _check_latex_template_id(self):
        for record in self:
            if record.report_type == "latex" and not record.latex_template_id:
                raise UserError(_("No LaTeX template configured for this report"))
            if (
                record.report_type == "latex"
                and record.latex_template_id
                and not record.latex_template_id.is_root
            ):
                raise UserError(_("The LaTeX template must be a root template"))

    def _render_latex(self, reportname, res_ids, data=None):
        """Generate PDF from LaTeX template."""
        report = self._get_report_from_name(reportname)
        report.ensure_one()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            combined_tex_file = report._gather_render_combine(
                temp_path, res_ids, render=True
            )
            if res_ids:
                res_id = res_ids[0]
                combined_content = combined_tex_file.read_text(encoding="utf-8")
                source = report._store_latex_source(combined_content, res_id, temp_path)
            source.compile_to_pdf(temp_path)
            return source.pdf_attachment_id.raw, "pdf"

    def _gather_render_combine(self, temp_path, res_ids, render=True):
        template_files = self._gather_latex_files(temp_path)
        main_tex_file = self.latex_template_id.file_name  # relative path
        if res_ids and render:
            for file_path in template_files:
                if file_path.suffix == ".tex":
                    content = file_path.read_text(encoding="utf-8")
                    rendered_content = self._render_latex_template(content, res_ids)
                    file_path.write_text(rendered_content, encoding="utf-8")
        combined_tex_file = temp_path / "combined.tex"  # absolute path
        output = subprocess.check_output(  # noqa: S603
            ["/usr/bin/latexpand", main_tex_file],
            stderr=subprocess.PIPE,
            cwd=temp_path,  # latexpand must be run in the temp directory
            text=True,
        )
        combined_tex_file.write_text(output, encoding="utf-8")
        return combined_tex_file

    def _gather_latex_files(self, temp_path):
        """Recursively gather all templates and subtemplates into temp directory."""
        self.ensure_one()
        files = []
        all_templates = self.latex_template_id
        templates_to_process = self.latex_template_id.subtemplate_ids

        while templates_to_process:
            all_templates += templates_to_process
            children = templates_to_process.mapped("subtemplate_ids")
            templates_to_process = children - all_templates

        # Write all template files
        for template in all_templates:
            template_file = temp_path / template.file_name
            template_file.write_text(template.content, encoding="utf-8")
            files.append(template_file)

        # Copy all attachments
        all_attachments = all_templates.mapped("attachment_ids")
        for attachment in all_attachments:
            if attachment.datas:
                attachment_file = temp_path / attachment.name
                attachment_file.write_bytes(attachment.raw)

        return files

    def _render_latex_template(self, content, res_ids):
        """Render LaTeX template using Jinja2."""
        env = Environment(
            loader=FileSystemLoader("."),
            block_start_string="%{",
            block_end_string="}%",
            variable_start_string="\\VAR{",
            variable_end_string="}",
            comment_start_string="%#",
            comment_end_string="#%",
            line_statement_prefix="%%",
            line_comment_prefix="%#",
            trim_blocks=True,
            autoescape=True,
        )
        objects = self.env[self.model].browse(res_ids)
        main_object = objects[0] if objects else None
        context = {
            "object": main_object,
            "objects": objects,
            "user": self.env.user,
            "company": self.env.company,
            "time": __import__("time"),
            "datetime": __import__("datetime"),
        }

        jinja_template = env.from_string(content)
        return jinja_template.render(**context)

    def _store_latex_source(self, combined_content, res_id, temp_path):
        """Store the combined LaTeX source in latex.source record."""
        source = self.env["latex.source"].search(
            [
                ("res_model", "=", self.model),
                ("res_id", "=", res_id),
                ("template_id", "=", self.latex_template_id.id),
            ],
            limit=1,
        )
        if source:
            source.write({"content": combined_content})
        else:
            res_record = self.env[self.model].browse(res_id)
            source_vals = {
                "name": f"{self.name} - {res_record.display_name}",
                "content": combined_content,
                "template_id": self.latex_template_id.id,
                "res_model": self.model,
                "res_id": res_id,
            }
            source = self.env["latex.source"].create(source_vals)
            source._create_assets_attachment(temp_path)
        return source

    def gen_report_download_filename(self, res_ids, data):
        if self.print_report_name and not len(res_ids) > 1:
            obj = self.env[self.model].browse(res_ids)
            return safe_eval(self.print_report_name, {"object": obj, "time": time})
        return f"{self.name}.pdf"
