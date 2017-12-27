# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).


from io import BytesIO
import os
from contextlib import closing
import logging
import tempfile
from subprocess import Popen, PIPE
from odoo import api, models, tools

_logger = logging.getLogger(__name__)
try:
    from fdfgen import forge_fdf
    EXTERNAL_DEPENDENCY_BINARY_PDFTK = tools.find_in_path('pdftk')
except (ImportError, IOError) as err:
    _logger.debug('Error while importing: %s.' % err)
    EXTERNAL_DEPENDENCY_BINARY_PDFTK = ""


class ReportFillPDFAbstract(models.AbstractModel):
    _name = 'report.report_fillpdf.abstract'

    def fill_report(self, docids, data):
        objs = self.env[self.env.context.get('active_model')].browse(docids)
        return self.fill_pdf_form(
            self.get_form(data, objs),
            self.get_document_values(data, objs)), 'pdf'

    @api.model
    def get_original_document_path(self, data, objs):
        raise NotImplementedError()

    @api.model
    def get_form(self, data, objs):
        with open(self.get_original_document_path(data, objs), 'rb') as file:
            result = file.read()
        return result

    @api.model
    def get_document_values(self, data, objs):
        return {}

    @api.model
    def fill_pdf_form(self, form, vals):
        fdf = forge_fdf("", vals.items(), [], [], [])
        document_fd, document_path = tempfile.mkstemp(
            suffix='.pdf', prefix='')
        with closing(os.fdopen(document_fd, 'wb')) as body_file:
            body_file.write(form)
        args = [
            EXTERNAL_DEPENDENCY_BINARY_PDFTK,
            document_path,
            "fill_form", "-",
            "output", "-",
            "dont_ask",
            "flatten"
        ]
        p = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate(fdf)
        os.unlink(document_path)
        if stderr.strip():
            raise IOError(stderr)
        return BytesIO(stdout).getvalue()
