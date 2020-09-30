# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo.tests.common import TransactionCase


class TestReportContext(TransactionCase):
    def test_report_01(self):
        company = self.browse_ref("base.main_company")
        report = self.browse_ref("web.action_report_internalpreview")
        self.env["ir.config_parameter"].sudo().set_param(
            "report.default.context", '{"test_parameter": 1}'
        )
        report.write({"context": '{"test_parameter": 2}'})
        action = report.with_context(test_parameter=3).report_action(company)
        self.assertEqual(
            3, action["context"]["report_action"]["context"]["test_parameter"]
        )

    def test_report_02(self):
        company = self.browse_ref("base.main_company")
        report = self.browse_ref("web.action_report_internalpreview")
        self.env["ir.config_parameter"].sudo().set_param(
            "report.default.context", '{"test_parameter": 1}'
        )
        report.write({"context": '{"test_parameter": 2}'})
        action = report.report_action(company)
        self.assertEqual(
            2, action["context"]["report_action"]["context"]["test_parameter"]
        )

    def test_report_03(self):
        company = self.browse_ref("base.main_company")
        report = self.browse_ref("web.action_report_internalpreview")
        self.env["ir.config_parameter"].sudo().set_param(
            "report.default.context", '{"test_parameter": 1}'
        )
        action = report.with_context(test_parameter=3).report_action(company)
        self.assertEqual(
            3, action["context"]["report_action"]["context"]["test_parameter"]
        )

    def test_report_04(self):
        company = self.browse_ref("base.main_company")
        report = self.browse_ref("web.action_report_internalpreview")
        report.write({"context": '{"test_parameter": 2}'})
        action = report.report_action(company)
        self.assertEqual(
            2, action["context"]["report_action"]["context"]["test_parameter"]
        )

    def test_report_05(self):
        company = self.browse_ref("base.main_company")
        report = self.browse_ref("web.action_report_internalpreview")
        self.env["ir.config_parameter"].sudo().set_param(
            "report.default.context", '{"test_parameter": 1}'
        )
        action = report.report_action(company)
        self.assertEqual(
            1, action["context"]["report_action"]["context"]["test_parameter"]
        )
