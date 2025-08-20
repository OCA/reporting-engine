# Copyright 2015 Tecnativa - Antonio Espinosa
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import logging

from odoo import fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools.safe_eval import safe_eval, time

from .signature import PdfSigner

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    certificate_id = fields.Many2one(
        comodel_name="certificate.certificate",
        company_dependent=True,
    )
    signing_domain = fields.Char(
        help="Domain for filtering if sign or not the document",
    )
    signing_allow_only_one = fields.Boolean(
        string="Allow to sign only one document",
        default=True,
        help="Disallow to sign a pdf composed of several documents",
    )
    signed_attachment = fields.Char(
        string="Save as attachment",
        help="Filename used to store signed document as attachment. "
        "Keep empty to not save signed document.",
    )

    def _is_report_type_signable(self):
        self.ensure_one()
        return self.report_type == "qweb-pdf" and self.certificate_id

    def _should_be_signed(self, res_ids):
        """Not all the documents should be rendered. Let's find out the right ones"""
        if not self._is_report_type_signable():
            return False
        if self.signing_allow_only_one and len(res_ids) > 1:
            _logger.debug(
                "This report allows to sign one document by pdf and this one is has %d",
                len(res_ids),
            )
            return False
        if self.signing_domain:
            domain = [("id", "in", tuple(res_ids))]
            domain = domain + safe_eval(self.signing_domain)
            docs = self.env[self.model_id.model].search(domain)
            if not docs:
                _logger.debug("Report signing domain not satisfied")
                return False
        return True

    def _attach_filename_get(self, res_ids):
        if len(res_ids) != 1:
            return False
        doc = self.env[self.model_id.model].browse(res_ids[0])
        return safe_eval(self.signed_attachment, {"object": doc, "time": time})

    def _attach_signed_read(self, res_ids):
        if len(res_ids) != 1:
            return False
        filename = self._attach_filename_get(res_ids)
        if not filename:
            return False
        attachment = self.env["ir.attachment"].search(
            [
                ("name", "=", filename),
                ("res_model", "=", self.model_id.model),
                ("res_id", "=", res_ids[0]),
            ],
            limit=1,
        )
        if attachment:
            return base64.b64decode(attachment.datas)
        return False

    def _attach_signed_write(self, res_ids, signed):
        if len(res_ids) != 1:
            return False
        filename = self._attach_filename_get(res_ids)
        if not filename:
            return False
        try:
            attachment = self.env["ir.attachment"].create(
                {
                    "name": filename,
                    "datas": base64.b64encode(signed),
                    "res_model": self.model_id.model,
                    "res_id": res_ids[0],
                }
            )
        except AccessError as exc:
            raise UserError(
                self.env._(
                    "Saving signed report (PDF): "
                    "You do not have enough access rights to save attachments"
                )
            ) from exc
        return attachment

    def _read_attached_signed_content(self, report, res_ids):
        signed_content, ext = False, False
        if self.signed_attachment:
            signed_content = self._attach_signed_read(res_ids)
            if signed_content:
                _logger.debug(
                    "The signed PDF document '%s/%s' was loaded from the database",
                    report.report_name,
                    res_ids,
                )
                return signed_content, "pdf"
        return signed_content, ext

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        report = self._get_report(report_ref)
        should_be_signed = report._should_be_signed(res_ids)
        signed_content, ext = self._read_attached_signed_content(report, res_ids)
        if signed_content:
            return signed_content, "pdf"
        content, ext = super()._render_qweb_pdf(report_ref, res_ids=res_ids, data=data)
        if should_be_signed:
            sign = PdfSigner(content, report.certificate_id)
            content = sign.sign_pdf()
            if report.signed_attachment:
                report._attach_signed_write(res_ids, content)
        return content, ext
