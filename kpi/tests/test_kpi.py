# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from unittest import mock

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestKPI(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))

    def _create_kpi(self, **values):
        category = self.env["kpi.category"].create({"name": "Test category"})
        threshold = self.env["kpi.threshold"].create({"name": "Test threshold"})
        defaults = {
            "name": "Test KPI",
            "category_id": category.id,
            "threshold_id": threshold.id,
            "periodicity": 1,
            "periodicity_uom": "day",
            "kpi_type": "python",
            "kpi_code": "1.0",
        }
        defaults.update(values)
        return self.env["kpi"].create(defaults)

    def test_invalid_threshold_range(self):
        range1 = self.env["kpi.threshold.range"].create(
            {
                "name": "Range1",
                "min_type": "static",
                "max_type": "static",
                "min_fixed_value": 3,
                "max_fixed_value": 1,
            }
        )
        range2 = self.env["kpi.threshold.range"].create(
            {
                "name": "Range2",
                "min_type": "static",
                "max_type": "static",
                "min_fixed_value": 4,
                "max_fixed_value": 10,
            }
        )
        self.assertFalse(range1.valid)
        self.assertTrue(range2.valid)

    def test_invalid_threshold(self):
        range1 = self.env["kpi.threshold.range"].create(
            {
                "name": "Range1",
                "min_type": "static",
                "max_type": "static",
                "min_fixed_value": 1,
                "max_fixed_value": 4,
            }
        )
        range2 = self.env["kpi.threshold.range"].create(
            {
                "name": "Range2",
                "min_type": "static",
                "max_type": "static",
                "min_fixed_value": 4,
                "max_fixed_value": 10,
            }
        )
        range3 = self.env["kpi.threshold.range"].create(
            {
                "name": "Range3",
                "min_type": "static",
                "max_type": "static",
                "min_fixed_value": 1,
                "max_fixed_value": 3,
            }
        )
        range_invalid = self.env["kpi.threshold.range"].create(
            {
                "name": "RangeInvalid",
                "min_type": "static",
                "max_type": "static",
                "min_fixed_value": 3,
                "max_fixed_value": 1,
            }
        )

        threshold1 = self.env["kpi.threshold"].create(
            {"name": "Threshold1", "range_ids": [(6, 0, [range1.id, range2.id])]}
        )

        threshold2 = self.env["kpi.threshold"].create(
            {"name": "Threshold2", "range_ids": [(6, 0, [range3.id, range2.id])]}
        )

        threshold3 = self.env["kpi.threshold"].create(
            {
                "name": "Threshold3",
                "range_ids": [(6, 0, [range_invalid.id, range2.id])],
            }
        )

        self.assertFalse(threshold1.valid)
        self.assertTrue(threshold2.valid)
        self.assertFalse(threshold3.valid)

    def test_threshold_create_with_range_commands(self):
        """Threshold create accepts Odoo 19 many2many command format."""
        range1 = self.env["kpi.threshold.range"].create(
            {
                "name": "Range A",
                "min_type": "static",
                "max_type": "static",
                "min_fixed_value": 0,
                "max_fixed_value": 5,
            }
        )
        range2 = self.env["kpi.threshold.range"].create(
            {
                "name": "Range B",
                "min_type": "static",
                "max_type": "static",
                "min_fixed_value": 6,
                "max_fixed_value": 10,
            }
        )
        threshold = self.env["kpi.threshold"].create(
            {
                "name": "Threshold commands",
                "range_ids": [(6, 0, [range1.id, range2.id])],
            }
        )
        self.assertTrue(threshold.valid)

    def test_invalid_threshold_range_exception(self):
        range_error = self.env["kpi.threshold.range"].create(
            {
                "name": "RangeError",
                "min_type": "python",
                "min_code": "<Not a valid python expression>",
                "max_type": "static",
                "max_fixed_value": 1,
            }
        )
        self.assertFalse(range_error.valid)

    def test_threshold_get_color(self):
        threshold_range = self.env["kpi.threshold.range"].create(
            {
                "name": "Green range",
                "min_type": "static",
                "max_type": "static",
                "min_fixed_value": 0,
                "max_fixed_value": 10,
                "color": "#00FF00",
            }
        )
        threshold = self.env["kpi.threshold"].create(
            {"name": "Threshold", "range_ids": [(6, 0, [threshold_range.id])]}
        )
        self.assertEqual(threshold.get_color(5), "#00FF00")
        self.assertEqual(threshold.get_color(15), "#FFFFFF")

    def test_kpi_python_scalar(self):
        kpi_category = self.env["kpi.category"].create({"name": "Scalar KPIs"})
        threshold_range = self.env["kpi.threshold.range"].create(
            {
                "name": "Range",
                "min_type": "static",
                "max_type": "static",
                "min_fixed_value": 0,
                "max_fixed_value": 10,
                "color": "#FF0000",
            }
        )
        kpi_threshold = self.env["kpi.threshold"].create(
            {
                "name": "KPI Threshold for scalar KPIs",
                "range_ids": [(6, 0, [threshold_range.id])],
            }
        )
        kpi = self.env["kpi"].create(
            {
                "name": "Scalar python kpi",
                "category_id": kpi_category.id,
                "threshold_id": kpi_threshold.id,
                "periodicity": 1,
                "periodicity_uom": "day",
                "kpi_type": "python",
                "kpi_code": "5.0",
            }
        )
        history_vals = kpi._get_kpi_value()
        self.assertEqual(history_vals["value"], 5.0)
        self.assertEqual(history_vals["color"], "#FF0000")

    def test_kpi_local_sql(self):
        kpi_category = self.env["kpi.category"].create({"name": "SQL KPIs"})
        kpi_threshold = self.env["kpi.threshold"].create(
            {"name": "KPI Threshold for SQL KPIs"}
        )
        kpi = self.env["kpi"].create(
            {
                "name": "SQL kpi",
                "category_id": kpi_category.id,
                "threshold_id": kpi_threshold.id,
                "periodicity": 1,
                "periodicity_uom": "day",
                "kpi_type": "local",
                "kpi_code": "SELECT 7 AS value",
            }
        )
        history_vals = kpi._get_kpi_value()
        self.assertEqual(history_vals["value"], 7)

    def test_kpi_python(self):
        kpi_category = self.env["kpi.category"].create({"name": "Dynamic KPIs"})
        kpi_threshold = self.env["kpi.threshold"].create(
            {"name": "KPI Threshold for dynamic KPIs"}
        )
        kpi_code = """
            {
                'value': 1.0,
                'color': '#00FF00'
            }
        """
        kpi = self.env["kpi"].create(
            {
                "name": "Dynamic python kpi",
                "description": "Dynamic python kpi",
                "category_id": kpi_category.id,
                "threshold_id": kpi_threshold.id,
                "periodicity": 1,
                "periodicity_uom": "day",
                "kpi_type": "python",
                "kpi_code": kpi_code,
            }
        )
        kpi.update_kpi_value()
        kpi_history = self.env["kpi.history"].search([("kpi_id", "=", kpi.id)])
        self.assertEqual(len(kpi_history), 1)
        self.assertEqual(kpi_history.color, "#00FF00")
        self.assertEqual(kpi_history.value, 1.0)

    def test_threshold_create_overlap_raises(self):
        range_low = self.env["kpi.threshold.range"].create(
            {
                "name": "Low",
                "min_type": "static",
                "max_type": "static",
                "min_fixed_value": 0,
                "max_fixed_value": 60,
            }
        )
        range_high = self.env["kpi.threshold.range"].create(
            {
                "name": "High",
                "min_type": "static",
                "max_type": "static",
                "min_fixed_value": 50,
                "max_fixed_value": 100,
            }
        )
        with self.assertRaises(ValidationError):
            self.env["kpi.threshold"].create(
                {
                    "name": "Overlapping threshold",
                    "range_ids": [(6, 0, [range_low.id, range_high.id])],
                }
            )

    def test_compute_display_last_kpi_value(self):
        kpi = self._create_kpi(kpi_code="42.0")
        self.assertEqual(kpi.value, 0)
        self.assertFalse(kpi.last_execution)
        kpi.compute_kpi_value()
        self.assertEqual(kpi.value, 42.0)
        self.assertTrue(kpi.last_execution)

    def test_update_next_execution_date(self):
        kpi = self._create_kpi(periodicity=2, periodicity_uom="day")
        self.assertFalse(kpi.next_execution_date)
        kpi.update_next_execution_date()
        self.assertTrue(kpi.next_execution_date)

    def test_update_kpi_value_scheduler(self):
        kpi = self._create_kpi(kpi_code="3.0", active=True)
        self.env["kpi"].update_kpi_value()
        self.assertEqual(len(kpi.history_ids), 1)
        self.assertEqual(kpi.value, 3.0)
        self.assertTrue(kpi.next_execution_date)

    def test_kpi_external_with_mock(self):
        dbsource = self.env["base.external.dbsource"].create(
            {
                "name": "Test DB Source",
                "connector": "postgresql",
                "conn_string": "dbname=test user=test host=localhost password=%s",
                "password": "secret",
            }
        )
        kpi = self._create_kpi(
            kpi_type="external",
            dbsource_id=dbsource.id,
            kpi_code="SELECT 9 AS value",
        )
        with mock.patch.object(
            type(dbsource),
            "execute",
            return_value=[{"value": 9}],
        ):
            history_vals = kpi._get_kpi_value()
        self.assertEqual(history_vals["value"], 9)

    def test_kpi_local_sql_rejects_non_select(self):
        kpi = self._create_kpi(
            kpi_type="local",
            kpi_code="DELETE FROM res_partner",
        )
        history_vals = kpi._get_kpi_value()
        self.assertEqual(history_vals["value"], 0)

    def test_threshold_range_local_sql(self):
        threshold_range = self.env["kpi.threshold.range"].create(
            {
                "name": "SQL range",
                "min_type": "local",
                "min_code": "SELECT 1 AS value",
                "max_type": "local",
                "max_code": "SELECT 10 AS value",
            }
        )
        self.assertTrue(threshold_range.valid)
        self.assertEqual(threshold_range.min_value, 1)
        self.assertEqual(threshold_range.max_value, 10)
