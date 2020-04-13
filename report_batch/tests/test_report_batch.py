# Copyright (C) 2019 IBM Corp.
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import odoo.tests.common as test_common


class TestReportBatch(test_common.SingleTransactionCase):
    def setUp(self):
        super(TestReportBatch, self).setUp()
        self.report_picking_operations = self.env.ref("stock.action_report_picking")
        self.report_deliveryslip = self.env.ref("stock.report_deliveryslip")

    def test_report_batch(self):
        report_batch = self.env["ir.actions.report"].create(
            {
                "name": "Batch Report",
                "report_type": "qweb-pdf",
                "model": "stock.picking",
                "report_name": "my_custom_batch_report",
            }
        )
        report_batch.write(
            {
                "subreport_ids": [
                    (
                        6,
                        0,
                        [
                            self.report_picking_operations.id,
                            self.report_deliveryslip.id,
                        ],
                    )
                ]
            }
        )
