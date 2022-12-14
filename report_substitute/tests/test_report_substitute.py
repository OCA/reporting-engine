# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestReportSubstitute(TransactionCase):
    def setUp(self):
        # In the demo file we create a new report for ir.module.module model
        # with a substation rule from the original report action
        super(TestReportSubstitute, self).setUp()
        self.action_report = self.env.ref("base.ir_module_reference_print")
        self.res_ids = self.env.ref("base.module_base").ids
        self.substitution_rule = self.env.ref(
            "report_substitute.substitution_rule_demo_1"
        )
        self.env.company.external_report_layout_id = self.env.ref(
            "web.external_layout_standard"
        ).id

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
                "substitution_action_report_id": self.env.ref(
                    "report_substitute.substitution_report_print_2"
                ).id,
                "action_report_id": self.env.ref(
                    "report_substitute.substitution_report_print"
                ).id,
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
                    "action_report_id": self.env.ref(
                        "report_substitute.substitution_report_print"
                    ).id,
                    "substitution_action_report_id": self.env.ref(
                        "base.ir_module_reference_print"
                    ).id,
                }
            )
