# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from pyPdf import PdfFileReader
from StringIO import StringIO
from openerp.tests.common import HttpCase


class TestReportRenderChrome(HttpCase):
    def test_report_qweb_chrome_renderer(self):
        self.authenticate('admin', 'admin')
        # travis won't allow running the suid binary
        self.env['ir.config_parameter'].set_param(
            'report_qweb_chrome_renderer.chrome_extra_parameters',
            '--no-sandbox'
        )
        pdf = self.env['report'].get_pdf(
            self.env.ref('base.user_root'),
            'report_qweb_chrome_renderer.demo_report',
        )
        reader = PdfFileReader(StringIO(pdf))
        self.assertTrue(reader)
