from odoo.addons.web.controllers import main as report
from odoo.http import route
from werkzeug.urls import url_decode
import json
import logging
from io import BytesIO

_logger = logging.getLogger(__name__)
try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
except ImportError as err:
    _logger.debug(err)


class ReportController(report.ReportController):
    @route()
    def report_download(self, data, token):
        result = super().report_download(data, token)
        requestcontent = json.loads(data)
        url, type = requestcontent[0], requestcontent[1]
        if (
            type in ['qweb-pdf'] and
            result.headers['Content-Type'] == "application/pdf" and
            '?' in url
        ):
            url_data = dict(url_decode(url.split('?')[1]).items())
            if 'context' in url_data:
                context_data = json.loads(url_data['context'])
                if 'encrypt_password' in context_data:
                    # We need to encrypt here because this function is not
                    # passing context, so we need to implement this again

                    data = result.get_data()
                    output_pdf = PdfFileWriter()
                    in_buff = BytesIO(data)
                    pdf = PdfFileReader(in_buff)
                    output_pdf.appendPagesFromReader(pdf)
                    output_pdf.encrypt(context_data['encrypt_password'])
                    buff = BytesIO()
                    output_pdf.write(buff)
                    result.set_data(buff.getvalue())
        return result
