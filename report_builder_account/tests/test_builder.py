# Copyright 2026 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import Command
from odoo.tests import tagged

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


@tagged("post_install", "-at_install")
class TestBuilder(AccountTestInvoicingCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        move = cls.init_invoice(
            "out_invoice",
            partner=cls.partner_a,
            amounts=[1000],
            post=True,
            invoice_date="2023-01-01",
            company=cls.company_data["company"],
        )
        cls.init_invoice(
            "out_invoice",
            partner=cls.partner_b,
            amounts=[10000],
            post=True,
            invoice_date="2024-01-01",
            company=cls.company_data["company"],
        )
        # We are adding this move to see that it isn't added
        cls.init_invoice(
            "out_invoice",
            partner=cls.partner_a,
            amounts=[100000],
            post=True,
            invoice_date="2025-01-01",
            company=cls.company_data["company"],
        )
        cls.init_invoice(
            "out_refund",
            partner=cls.partner_a,
            amounts=[1],
            post=True,
            invoice_date="2023-01-01",
            company=cls.company_data["company"],
        )
        cls.init_invoice(
            "out_refund",
            partner=cls.partner_b,
            amounts=[10],
            post=True,
            invoice_date="2024-01-01",
            company=cls.company_data["company"],
        )
        # We are adding this move to see that it isn't added
        cls.init_invoice(
            "out_refund",
            amounts=[100],
            partner=cls.partner_a,
            post=True,
            invoice_date="2025-01-01",
            company=cls.company_data["company"],
        )
        code = move.invoice_line_ids.account_id.code[:3]
        cls.template = cls.env["report.template"].create(
            {
                "name": "Test Template",
                "source": "account",
                "search_model_id": cls.env.ref("account.model_account_move_line").id,
                "search_view_id": cls.env.ref(
                    "account.view_account_move_line_filter"
                ).id,
                "kpi_ids": [
                    Command.create(
                        {
                            "name": "Test KPI",
                            "item_ids": [
                                Command.create(
                                    {
                                        "kind": "query",
                                        "code": f"{code}%",
                                        "query_kind_id": cls.env.ref(
                                            "report_builder_account.kpi_kind_balp"
                                        ).id,
                                    }
                                )
                            ],
                        }
                    )
                ],
            }
        )
        cls.kpi = cls.template.kpi_ids
        cls.item = cls.template.kpi_ids.item_ids
        cls.instance = cls.env["report.instance"].create(
            {
                "name": "Test Instance",
                "template_id": cls.template.id,
                "column_ids": [
                    Command.create(
                        {
                            "name": "CY",
                            "date_from": "2024-01-01",
                            "date_to": "2024-12-31",
                            "mode": "date",
                        }
                    )
                ],
            }
        )

    def test_balp(self):
        self.assertEqual(
            self.instance.process_information("2024-01-01")[self.kpi.id][
                self.instance.column_ids.id
            ]["total"],
            -9990,
        )

    def test_bale(self):
        self.item.query_kind_id = self.env.ref("report_builder_account.kpi_kind_bale")
        self.assertEqual(
            self.instance.process_information("2024-01-01")[self.kpi.id][
                self.instance.column_ids.id
            ]["total"],
            -10989,
        )

    def test_bali(self):
        self.item.query_kind_id = self.env.ref("report_builder_account.kpi_kind_bali")
        self.assertEqual(
            self.instance.process_information("2024-01-01")[self.kpi.id][
                self.instance.column_ids.id
            ]["total"],
            -999,
        )

    def test_crdp(self):
        self.item.query_kind_id = self.env.ref("report_builder_account.kpi_kind_crdp")
        self.assertEqual(
            self.instance.process_information("2024-01-01")[self.kpi.id][
                self.instance.column_ids.id
            ]["total"],
            10000,
        )

    def test_crde(self):
        self.item.query_kind_id = self.env.ref("report_builder_account.kpi_kind_crde")
        self.assertEqual(
            self.instance.process_information("2024-01-01")[self.kpi.id][
                self.instance.column_ids.id
            ]["total"],
            11000,
        )

    def test_crdi(self):
        self.item.query_kind_id = self.env.ref("report_builder_account.kpi_kind_crdi")
        self.assertEqual(
            self.instance.process_information("2024-01-01")[self.kpi.id][
                self.instance.column_ids.id
            ]["total"],
            1000,
        )

    def test_debp(self):
        self.item.query_kind_id = self.env.ref("report_builder_account.kpi_kind_debp")
        self.assertEqual(
            self.instance.process_information("2024-01-01")[self.kpi.id][
                self.instance.column_ids.id
            ]["total"],
            10,
        )

    def test_debe(self):
        self.item.query_kind_id = self.env.ref("report_builder_account.kpi_kind_debe")
        self.assertEqual(
            self.instance.process_information("2024-01-01")[self.kpi.id][
                self.instance.column_ids.id
            ]["total"],
            11,
        )

    def test_debi(self):
        self.item.query_kind_id = self.env.ref("report_builder_account.kpi_kind_debi")
        self.assertEqual(
            self.instance.process_information("2024-01-01")[self.kpi.id][
                self.instance.column_ids.id
            ]["total"],
            1,
        )

    def test_report_filter(self):
        self.assertEqual(
            self.instance.process_information(
                "2024-01-01", [("partner_id", "=", self.partner_b.id)]
            )[self.kpi.id][self.instance.column_ids.id]["total"],
            -9990,
        )
        self.assertEqual(
            self.instance.process_information(
                "2024-01-01", [("partner_id", "=", self.partner_a.id)]
            )[self.kpi.id][self.instance.column_ids.id]["total"],
            0,
        )

    def test_item_filter(self):
        self.item.domain = f"[('partner_id', '=', {self.partner_b.id})]"
        self.assertEqual(
            self.instance.process_information(
                "2024-01-01",
            )[self.kpi.id][self.instance.column_ids.id]["total"],
            -9990,
        )
        self.item.domain = f"[('partner_id', '=', {self.partner_a.id})]"
        self.assertEqual(
            self.instance.process_information(
                "2024-01-01",
            )[self.kpi.id][self.instance.column_ids.id]["total"],
            0,
        )
