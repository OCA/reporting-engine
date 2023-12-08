# Copyright 2020 Creu Blanca
# Copyright 2020 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from io import BytesIO

from PyPDF2 import PdfFileReader, PdfFileWriter

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    encrypt = fields.Selection(
        [("manual", "Manual Input Password"), ("auto", "Auto Generated Password")],
        string="Encryption",
        help="* Manual Input Password: allow user to key in password on the fly. "
        "This option available only on document print action.\n"
        "* Auto Generated Password: system will auto encrypt password when PDF "
        "created, based on provided python syntax.",
    )
    encrypt_password = fields.Char(
        help="Python code syntax to gnerate password.",
    )

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        document, ttype = super()._render_qweb_pdf(
            report_ref, res_ids=res_ids, data=data
        )
        report = self._get_report(report_ref)
        if res_ids:
            encrypt_password = self._context.get("encrypt_password")
            report = self._get_report_from_name(report.report_name).with_context(
                encrypt_password=encrypt_password
            )
            password = report._get_pdf_password(res_ids[:1])
            document = self._encrypt_pdf(document, password)
        return document, ttype

    def _get_pdf_password(self, res_ids):
        encrypt_password = False
        if self.encrypt == "manual":
            # If use document print action, report_download() is called,
            # but that can't pass context (encrypt_password) here.
            # As such, file will be encrypted by report_download() again.
            # --
            # Following is used just in case when context is passed in.
            encrypt_password = self._context.get("encrypt_password", False)
        elif self.encrypt == "auto" and self.encrypt_password:
            # access the report details with sudo() but evaluation context as sudo(False)
            self_sudo = self.sudo()

            Model = self.env[self_sudo.model]
            record_ids = Model.browse(res_ids)
            try:
                encrypt_password = safe_eval(
                    self.encrypt_password, {"object": record_ids}
                )
            except Exception as e:
                raise ValidationError(
                    _(
                        "Python code used for encryption password is invalid.\n%s",
                        self.encrypt_password,
                    )
                ) from e
        return encrypt_password

    @staticmethod
    def _encrypt_pdf(data, password):
        if not password:
            return data
        output_pdf = PdfFileWriter()
        in_buff = BytesIO(data)
        pdf = PdfFileReader(in_buff)
        output_pdf.appendPagesFromReader(pdf)
        output_pdf.encrypt(password)
        buff = BytesIO()
        output_pdf.write(buff)
        return buff.getvalue()

    def _get_readable_fields(self):
        return super()._get_readable_fields() | {"encrypt"}
