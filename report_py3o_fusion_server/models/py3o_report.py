# © 2013 XCG Consulting <http://odoo.consulting>
# © 2016 ACSONE SA/NV
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import json
import logging
import os
import tempfile
from contextlib import closing
from datetime import datetime
from io import BytesIO

import requests

from odoo import _, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)

try:
    from py3o.template import Template
    from py3o.template.helpers import Py3oConvertor
except ImportError:
    logger.debug("Cannot import py3o.template")


class Py3oReport(models.TransientModel):
    _inherit = "py3o.report"

    def _create_single_report(self, model_instance, data):
        """This function to generate our py3o report"""
        self.ensure_one()
        report_xml = self.ir_actions_report_id
        filetype = report_xml.py3o_filetype
        if not report_xml.py3o_server_id:
            return super()._create_single_report(model_instance, data)
        elif report_xml.py3o_is_local_fusion:
            result_path = super(
                Py3oReport, self.with_context(report_py3o_skip_conversion=True)
            )._create_single_report(model_instance, data)
            with closing(open(result_path, "rb")) as out_stream:
                tmpl_data = out_stream.read()
            datadict = {}
        else:
            result_fd, result_path = tempfile.mkstemp(
                suffix="." + filetype, prefix="p3o.report.tmp."
            )
            tmpl_data = self.get_template(model_instance)

            in_stream = BytesIO(tmpl_data)
            with closing(os.fdopen(result_fd, "wb+")) as out_stream:
                template = Template(in_stream, out_stream, escape_false=True)
                localcontext = self._get_parser_context(model_instance, data)
                expressions = template.get_all_user_python_expression()
                py_expression = template.convert_py3o_to_python_ast(expressions)
                convertor = Py3oConvertor()
                data_struct = convertor(py_expression)
                datadict = data_struct.render(localcontext)

        # Call py3o.server to render the template in the desired format
        files = {"tmpl_file": tmpl_data}
        fields = {
            "targetformat": filetype,
            "datadict": json.dumps(datadict),
            "image_mapping": "{}",
            "escape_false": "on",
        }
        if report_xml.py3o_is_local_fusion:
            fields["skipfusion"] = "1"
        url = report_xml.py3o_server_id.url
        logger.info(
            "Connecting to %s to convert report %s to %s",
            url,
            report_xml.report_name,
            filetype,
        )
        if filetype == "pdf":
            options = (
                report_xml.pdf_options_id or report_xml.py3o_server_id.pdf_options_id
            )
            if options:
                pdf_options_dict = options.odoo2libreoffice_options()
                fields["pdf_options"] = json.dumps(pdf_options_dict)
                logger.debug("PDF Export options: %s", pdf_options_dict)
        start_chrono = datetime.now()
        r = requests.post(url, data=fields, files=files, timeout=10)
        if r.status_code != 200:
            # server says we have an issue... let's tell that to enduser
            logger.error("Py3o fusion server error: %s", r.text)
            raise UserError(_("Fusion server error %s") % r.text)

        chunk_size = 1024
        with open(result_path, "w+b") as fd:
            for chunk in r.iter_content(chunk_size):
                fd.write(chunk)
        end_chrono = datetime.now()
        convert_seconds = (end_chrono - start_chrono).total_seconds()
        logger.info(
            "Report %s converted to %s in %s seconds",
            report_xml.report_name,
            filetype,
            convert_seconds,
        )
        if len(model_instance) == 1:
            self._postprocess_report(model_instance, result_path)
        return result_path
