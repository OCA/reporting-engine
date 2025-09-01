# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
import io
import logging
import os
import subprocess
import tempfile
import zipfile
from pathlib import Path

from odoo import _, api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class LatexSource(models.Model):
    _name = "latex.source"
    _inherit = ["latex.record.mixin", "mail.thread"]
    _description = "Latex source"

    name = fields.Char(required=True)
    content = fields.Text(required=True)
    template_id = fields.Many2one(
        comodel_name="latex.template", required=True, readonly=True
    )

    version = fields.Integer(default=0, readonly=True)
    previous_version = fields.Text(readonly=True)
    modified_content = fields.Boolean(compute="_compute_modified_content")
    version_history = fields.Json(readonly=True)

    pdf_attachment_id = fields.Many2one(comodel_name="ir.attachment", readonly=True)
    assets_attachment_id = fields.Many2one(comodel_name="ir.attachment", readonly=True)
    pdf_data = fields.Binary(
        string="PDF", related="pdf_attachment_id.datas", readonly=True
    )
    assets_data = fields.Binary(
        string="Zipped Assets", related="assets_attachment_id.datas", readonly=True
    )

    @api.depends("content", "previous_version")
    def _compute_modified_content(self):
        for record in self:
            record.modified_content = record.content != record.previous_version

    def _set_new_version(self):
        self.ensure_one()
        self.version += 1
        self.previous_version = self.content
        history = self.version_history or {}
        history[self.version] = self.content
        self.version_history = history
        return self.version

    def action_download_zip(self):
        """Download the assets zip file."""
        self.ensure_one()
        if not self.assets_attachment_id:
            raise UserError(_("No assets available for download"))

        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self.assets_attachment_id.id}?download=true",
            "target": "new",
        }

    def action_compile_to_pdf(self):
        self.ensure_one()
        self.compile_to_pdf()
        return {
            "type": "ir.actions.act_url",
            "url": f"/web/content/{self.pdf_attachment_id.id}?download=true",
            "target": "new",
        }

    def compile_to_pdf(self, temp_path=None):
        self.ensure_one()
        if self.modified_content or not self.pdf_attachment_id:
            self._set_new_version()
            if not temp_path:
                self._compile_to_pdf_from_assets()
            else:
                self._compile_to_pdf(temp_path)

    def _compile_to_pdf(self, temp_path):
        self.ensure_one()
        combined_tex_file = temp_path / "combined.tex"
        combined_tex_file.write_text(self.content, encoding="utf-8")
        pdf_content = self._compile_latex_to_pdf(combined_tex_file, temp_path)
        self._create_pdf_attachment(pdf_content)

    def _compile_to_pdf_from_assets(self):
        self.ensure_one()
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            self._extract_assets_to_temp(temp_path)
            self._compile_to_pdf(temp_path)

    def _extract_assets_to_temp(self, temp_path):
        zip_data = base64.b64decode(self.assets_attachment_id.datas)
        with zipfile.ZipFile(io.BytesIO(zip_data), "r") as zip_file:
            zip_file.extractall(temp_path)

    def _gather_template_assets(self, temp_path):
        all_templates = self.template_id
        templates_to_process = self.template_id.subtemplate_ids

        while templates_to_process:
            all_templates += templates_to_process
            children = templates_to_process.mapped("subtemplate_ids")
            templates_to_process = children - all_templates

        for template in all_templates:
            template_file = temp_path / template.file_name
            template_file.write_text(template.content, encoding="utf-8")

        all_attachments = all_templates.mapped("attachment_ids")
        for attachment in all_attachments:
            if attachment.datas:
                attachment_file = temp_path / attachment.name
                attachment_file.write_bytes(attachment.raw)

    def _create_assets_attachment(self, temp_path):
        """Create attachment with all assets."""
        zip_content = self._compress_folder(temp_path)

        attachment = self.env["ir.attachment"].create(
            {
                "name": f"{self.name}_assets.zip",
                "type": "binary",
                "datas": base64.b64encode(zip_content),
                "mimetype": "application/zip",
                "res_model": self._name,
                "res_id": self.id,
            }
        )
        self.assets_attachment_id = attachment.id

    def _create_pdf_attachment(self, pdf_content):
        """Create attachment with PDF content."""
        attachment = self.env["ir.attachment"].create(
            {
                "name": f"{self.name}_v{self.version}.pdf",
                "type": "binary",
                "datas": base64.b64encode(pdf_content),
                "mimetype": "application/pdf",
                "res_model": self._name,
                "res_id": self.id,
            }
        )
        self.pdf_attachment_id = attachment.id

    def _compress_folder(self, folder_path):
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    arcname = os.path.relpath(full_path, start=folder_path)
                    zip_file.write(full_path, arcname)
        zip_buffer.seek(0)
        return zip_buffer.getvalue()

    def _compile_latex_to_pdf(self, tex_file, temp_path):
        """Compile LaTeX file to PDF using pdflatex."""
        try:
            # Run pdflatex multiple times for proper references
            # Bibtex requires 3 times. make it configurable?
            # In any case, ToC requires 2 times, which is the base case
            for _i in range(2):
                subprocess.check_output(  # noqa: S603
                    [
                        "/usr/bin/pdflatex",
                        "-interaction=nonstopmode",
                        "-output-directory",
                        str(temp_path),
                        str(tex_file),
                    ],
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=temp_path,
                )
            pdf_file = temp_path / f"{tex_file.stem}.pdf"
            return pdf_file.read_bytes()

        except Exception as e:
            msg = _("LaTeX compilation error: %s")
            logger.error("LaTeX compilation error: %s", str(e))
            raise UserError(msg % str(e)) from e
