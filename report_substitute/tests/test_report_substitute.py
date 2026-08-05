# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReportSubstitute(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.action_report = cls.env.ref("base.ir_module_reference_print")
        cls.res_ids = cls.env.ref("base.module_base").ids
        cls.env.company.external_report_layout_id = cls.env.ref(
            "web.external_layout_standard"
        ).id

        cls.substitution_report_test_view = cls.env["ir.ui.view"].create(
            {
                "name": "substitution_report_test",
                "key": "substitution_report_test",
                "type": "qweb",
                "arch": '<t t-name="report_substitute.substitution_report_test">'
                '   <div class="page">Substitution Report</div>'
                "</t>",
            }
        )
        cls.env["ir.model.data"].create(
            {
                "model": "ir.ui.view",
                "module": "report_substitute",
                "name": "substitution_report_test",
                "res_id": cls.substitution_report_test_view.id,
            }
        )

        cls.substitution_report_2_test_view = cls.env["ir.ui.view"].create(
            {
                "key": "substitution_report_2_test",
                "name": "substitution_report_2_test",
                "type": "qweb",
                "arch": '<t t-name="report_substitute.substitution_report_2_test">'
                '   <div class="page">Substitution Report 2</div>'
                "</t>",
            }
        )
        cls.env["ir.model.data"].create(
            {
                "model": "ir.ui.view",
                "module": "report_substitute",
                "name": "substitution_report_2_test",
                "res_id": cls.substitution_report_2_test_view.id,
            }
        )

        cls.substitution_report = cls.env["ir.actions.report"].create(
            {
                "name": "Substitution For Technical guide",
                "model": "ir.module.module",
                "report_type": "qweb-pdf",
                "report_name": "report_substitute.substitution_report_test",
                "report_file": "report_substitute.substitution_report_test",
                "binding_type": "report",
            }
        )
        cls.substitution_report_2 = cls.env["ir.actions.report"].create(
            {
                "name": "Substitution 2 For Technical guide",
                "model": "ir.module.module",
                "report_type": "qweb-pdf",
                "report_name": "report_substitute.substitution_report_2_test",
                "report_file": "report_substitute.substitution_report_2_test",
                "binding_type": "report",
            }
        )
        cls.substitution_rule = cls.env["ir.actions.report.substitution.rule"].create(
            {
                "action_report_id": cls.action_report.id,
                "substitution_action_report_id": cls.substitution_report.id,
            }
        )

    def test_substitution(self):
        res = str(
            self.action_report._render(
                self.action_report.report_name, res_ids=self.res_ids
            )[0]
        )
        self.assertIn('<div class="page">Substitution Report</div>', res)
        # remove the substation rule
        self.substitution_rule.unlink()
        res = str(
            self.action_report._render(
                self.action_report.report_name, res_ids=self.res_ids
            )[0]
        )
        self.assertNotIn('<div class="page">Substitution Report</div>', res)

    def test_recursive_substitution(self):
        res = str(
            self.action_report._render(
                self.action_report.report_name, res_ids=self.res_ids
            )[0]
        )
        self.assertNotIn('<div class="page">Substitution Report 2</div>', res)
        self.env["ir.actions.report.substitution.rule"].create(
            {
                "substitution_action_report_id": self.substitution_report_2.id,
                "action_report_id": self.substitution_report.id,
            }
        )
        res = str(
            self.action_report._render(
                self.action_report.report_name, res_ids=self.res_ids
            )[0]
        )
        self.assertIn('<div class="page">Substitution Report 2</div>', res)

    def test_substitution_with_domain(self):
        self.substitution_rule.write({"domain": "[('name', '=', 'base')]"})
        res = str(
            self.action_report._render(
                self.action_report.report_name, res_ids=self.res_ids
            )[0]
        )
        self.assertIn('<div class="page">Substitution Report</div>', res)
        self.substitution_rule.write({"domain": "[('name', '!=', 'base')]"})
        res = str(
            self.action_report._render(
                self.action_report.report_name, res_ids=self.res_ids
            )[0]
        )
        self.assertNotIn('<div class="page">Substitution Report</div>', res)

    def test_substitution_with_action_dict(self):
        substitution_report_action = self.env[
            "ir.actions.report"
        ].get_substitution_report_action(self.action_report.read()[0], self.res_ids)
        self.assertEqual(
            substitution_report_action["id"],
            self.substitution_rule.substitution_action_report_id.id,
        )

    def test_substitution_with_report_action(self):
        res = self.action_report.report_action(self.res_ids)
        self.assertEqual(
            res["report_name"],
            self.substitution_rule.substitution_action_report_id.report_name,
        )

    def test_substitution_infinite_loop(self):
        with self.assertRaises(ValidationError):
            self.env["ir.actions.report.substitution.rule"].create(
                {
                    "action_report_id": self.substitution_report.id,
                    "substitution_action_report_id": self.action_report.id,
                }
            )
