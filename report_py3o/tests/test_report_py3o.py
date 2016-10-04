# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).).


import mock

from openerp.tests.common import TransactionCase
import openerp.tests


@openerp.tests.common.at_install(False)
@openerp.tests.common.post_install(True)
class TestReportPy3o(TransactionCase):

    def test_reports(self):
        report = self.env.ref("report_py3o.res_users_report_py3o")
        with mock.patch('openerp.addons.report_py3o.py3o_parser.'
                        'Py3oParser.create_single_pdf') as patched_pdf:
            # test the call the the create method inside our custom parser
            report.render_report(self.env.user.ids,
                                 report.report_name,
                                 {})
            self.assertEqual(1, patched_pdf.call_count)
        res = report.render_report(
            self.env.user.ids, report.report_name, {})
        self.assertTrue(res)
        py3o_server = self.env['py3o.server'].create({"url": "http://dummy"})
        # check the call to the fusion server
        report.write({"py3o_filetype": "pdf",
                      "py3o_server_id": py3o_server.id})
        with mock.patch('requests.post') as patched_post:
            magick_response = mock.MagicMock()
            magick_response.status_code = 200
            patched_post.return_value = magick_response
            magick_response.iter_content.return_value = "test result"
            res = report.render_report(
                self.env.user.ids, report.report_name, {})
            self.assertEqual(('test result', '.pdf'), res)
