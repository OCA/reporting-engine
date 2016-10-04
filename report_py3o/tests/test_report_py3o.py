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
