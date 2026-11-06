# Copyright 2015 Tecnativa - Antonio Espinosa
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import io
import logging

from odoo import fields, models
from odoo.exceptions import AccessError, UserError
from odoo.tools.pdf.signature import PdfSigner
from odoo.tools.safe_eval import safe_eval, time

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

    def _should_be_signed(self, res_ids: list) -> list:
        """Not all the documents should be rendered. Let's find out the right ones"""
        if not self._is_report_type_signable() or not res_ids:
            return []
        if (
            # In this case, we expect the ids to be splitted. I.e.: invoice mass send
            not self.env.context.get("pre_render_qweb_pdf")
            and self.signing_allow_only_one
            and len(res_ids) > 1
        ):
            _logger.warning(
                "This report allows to sign one document by pdf and this one is has %d",
                len(res_ids),
            )
            return []
        if self.signing_domain:
            res_ids = (
                self.env[self.model_id.model]
                .search([("id", "in", res_ids)] + safe_eval(self.signing_domain))
                .ids
            )
            if not res_ids:
                _logger.debug("Report signing domain not satisfied")
        return res_ids

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

    def _sign_pdf(self, content):
        """Sign the given PDF ``content`` (bytes) using Odoo's standard
        :class:`~odoo.tools.pdf.signature.PdfSigner`.

        The core signer loads the key/certificate from
        ``company.signing_certificate_id``. This module lets the certificate be
        configured per report, so we feed the report's ``certificate_id`` to the
        signer instead.
        """
        self.ensure_one()
        signer = PdfSigner(io.BytesIO(content), company=self.env.company)
        signer._load_key_and_certificate = (
            self.certificate_id._load_signing_key_and_cert
        )
        signed_stream = signer.sign_pdf()
        if not signed_stream:
            _logger.warning(
                "The PDF for report '%s' could not be signed", self.report_name
            )
            return content
        return signed_stream.getvalue()

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
            content = report._sign_pdf(content)
            if report.signed_attachment:
                report._attach_signed_write(res_ids, content)
        return content, ext

    def _pre_render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        # Evaluate signature id by id so we can use it later in the report splitting
        content, report_type = super()._pre_render_qweb_pdf(report_ref, res_ids, data)
        if report_type != "pdf":
            return content, report_type
        report = self._get_report(report_ref)
        should_be_signed = report.with_context(
            pre_render_qweb_pdf=True
        )._should_be_signed(res_ids)
        for res_id, stream_values in content.items():
            if res_id in should_be_signed:
                stream_values["sign"] = True
        return content, report_type

    def _get_splitted_report(self, report_ref, content, report_type):
        # Sign every document if needed
        res = super()._get_splitted_report(report_ref, content, report_type)
        if report_type != "pdf":
            return res
        report = self._get_report(report_ref)
        should_be_signed = {
            res_id for res_id, stream in content.items() if stream.get("sign")
        }
        for res_id, content in res.items():
            if res_id not in should_be_signed:
                continue
            res[res_id] = report._sign_pdf(content)
        return res
