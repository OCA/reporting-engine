# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestKPIDemo(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def test_demo_threshold_is_valid(self):
        threshold = self.env.ref(
            "kpi.kpi_threshold_demo_performance", raise_if_not_found=False
        )
        if not threshold:
            self.skipTest("Demo data is not loaded")
        self.assertTrue(threshold.valid)
        self.assertEqual(len(threshold.range_ids), 3)

    def test_demo_python_kpi_computation(self):
        kpi = self.env.ref("kpi.kpi_demo_satisfaction", raise_if_not_found=False)
        if not kpi:
            self.skipTest("Demo data is not loaded")
        kpi.compute_kpi_value()
        self.assertEqual(kpi.value, 85.0)
        self.assertEqual(kpi.color, "#00FF00")
        self.assertEqual(len(kpi.history_ids), 1)

    def test_demo_local_sql_kpi_computation(self):
        kpi = self.env.ref("kpi.kpi_demo_partner_count", raise_if_not_found=False)
        if not kpi:
            self.skipTest("Demo data is not loaded")
        kpi.compute_kpi_value()
        self.assertGreaterEqual(kpi.value, 1.0)
        self.assertTrue(kpi.history_ids)
