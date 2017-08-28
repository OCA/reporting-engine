# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from pyPdf import PdfFileReader
from StringIO import StringIO
from openerp.tests.common import HttpCase


class TestReportRenderChrome(HttpCase):
    def test_report_render_chrome(self):
        self.authenticate('admin', 'admin')
        pdf = self.env['report'].get_pdf(
            self.env.ref('base.user_root'), 'report_render_chrome.demo_report',
        )
        reader = PdfFileReader(StringIO(pdf))
        self.assertTrue(reader)
