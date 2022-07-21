# Copyright 2022 Openindustry.it (<https://openindustry.it>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import logging
import os
import subprocess
import tempfile

from odoo import _, api, fields, models
from odoo.tools.misc import find_in_path

logger = logging.getLogger(__name__)


class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_xlsx_to_pdf = fields.Boolean(
        string="Export to pdf format",
        default=False,
    )

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
        return cmd

    @api.model
    def _cleanup_tempfiles(self, temporary_files):
        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except OSError:
                logger.error("Error when trying to remove file %s" % temporary_file)
