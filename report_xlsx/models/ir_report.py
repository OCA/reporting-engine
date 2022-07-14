# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import os
import subprocess
import tempfile
from io import BytesIO

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.misc import find_in_path

logger = logging.getLogger(__name__)


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("xlsx", "XLSX")], ondelete={"xlsx": "set default"}
    )
    report_xlsx_to_pdf = fields.Boolean(
        string="Report xlsx to pdf",
        default=False,
    )

    @api.model
    def _render_xlsx(self, docids, data):
        report_model_name = "report.%s" % self.report_name
        report_model = self.env.get(report_model_name)
        if report_model is None:
            raise UserError(_("%s model was not found") % report_model_name)
        return (
            report_model.with_context(active_model=self.model)
            .sudo(False)
            .create_xlsx_report(docids, data)  # noqa
        )

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(ReportAction, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env["ir.actions.report"]
        qwebtypes = ["xlsx"]
        conditions = [
            ("report_type", "in", qwebtypes),
            ("report_name", "=", report_name),
        ]
        context = self.env["res.users"].context_get()
        return report_obj.with_context(context).search(conditions, limit=1)

    def _create_single_report(self, model_instance, data, xlsx):
        """This function to generate our pdf report"""
        self.ensure_one()
        result_fd, result_path = tempfile.mkstemp(
            suffix=".xlsx", prefix="xlsx.report.tmp."
        )
        os.write(result_fd, xlsx)
        result_path = self._convert_single_report(result_path, model_instance, data)
        with open(result_path, "rb") as fh:
            file_data = fh.read()
        return file_data

    def _convert_single_report(self, result_path, model_instance, data):
        """Run a command to convert to our target format"""
        with tempfile.TemporaryDirectory() as tmp_user_installation:
            command = self._convert_single_report_cmd(
                result_path,
                model_instance,
                data,
                user_installation=tmp_user_installation,
            )
            logger.debug("Running command %s", command)
            output = subprocess.check_output(command, cwd=os.path.dirname(result_path))
            logger.debug("Output was %s", output)
            self._cleanup_tempfiles([result_path])
            result_path, result_filename = os.path.split(result_path)
            result_path = os.path.join(
                result_path,
                "%s.%s"
                % (
                    os.path.splitext(result_filename)[0],
                    "pdf",
                ),
            )
        return result_path

    def _convert_single_report_cmd(
        self, result_path, model_instance, data, user_installation=None
    ):
        """Return a command list suitable for use in subprocess.call"""
        try:
            lo_bin = find_in_path("libreoffice")
        except IOError:
            lo_bin = None
        if not lo_bin:
            raise RuntimeError(
                _(
                    "Libreoffice runtime not available. "
                    "Please contact your administrator."
                )
            )
        cmd = [
            lo_bin,
            "--headless",
            "--convert-to",
            "pdf",
            result_path,
        ]
        # if user_installation:
        #    cmd.append("-env:UserInstallation=file:%s" % user_installation)
        return cmd

    def _postprocess_report(self, model_instance, result_path):
        if len(model_instance) == 1:
            with open(result_path, "rb") as f:
                buffer = BytesIO(f.read())
                self.ir_actions_report_id._postprocess_pdf_report(
                    model_instance, buffer
                )
        return result_path

    @api.model
    def _cleanup_tempfiles(self, temporary_files):
        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except OSError:
                logger.error("Error when trying to remove file %s" % temporary_file)
