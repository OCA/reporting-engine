# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import os
import unittest

from odoo.tests.common import TransactionCase


class TestLatexReport(TransactionCase):
    def setUp(self):
        super().setUp()
        self.user = self.env.ref("base.user_demo")
        self.template = self.env.ref("report_latex.demo_res_users_latex_template")
        self.report = self.env.ref("report_latex.demo_res_users_latex_report")

    @unittest.skipIf(not os.getenv("LaTeX"), "Compilation needs LaTeX packages")
    def test_latex_report(self):
        """Test LaTeX report generation."""
        data = {"options": None}
        report_ref = self.report.report_name
        res_ids = [self.user.id]
        result = self.report._render_latex(report_ref, res_ids, data=data)
        self.assertTrue(result[0], "LaTeX report should generate content")
        self.assertEqual(result[1], "pdf", "Result should be a PDF")
