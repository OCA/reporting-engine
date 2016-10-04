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
        domain = [('report_type', '=', 'py3o'),
                  ('report_name', '=', 'py3o_user_info')]
        reports = self.env['ir.actions.report.xml'].search(domain)
        self.assertEqual(1, len(reports))
        for r in reports:
            with mock.patch('openerp.addons.report_py3o.py3o_parser.'
                            'Py3oParser.create_single_pdf') as patched_pdf:
                r.render_report(self.env.user.ids,
                                r.report_name,
                                {})
                self.assertEqual(1, patched_pdf.call_count)
