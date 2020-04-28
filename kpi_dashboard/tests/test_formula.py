# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestFormula(TransactionCase):
    def test_computation(self):
        kpi = self.env["kpi.kpi"].create(
            {
                "name": "DEMO KPI",
                "widget": "number",
                "computation_method": "code",
            }
        )
        self.assertFalse(kpi.value)
        kpi.compute()
        self.assertEqual(kpi.value, {})
        kpi.code = """
result = {}
result['value'] = len(model.search([('id', '=', %s)]))
result['previous'] = len(model.search([('id', '!=', %s)]))
        """ % (
            kpi.id,
            kpi.id,
        )
        kpi.compute()
        value = kpi.value
        self.assertTrue(value.get("value"))
        self.assertEqual(value.get("value"), 1)
        self.assertEqual(value.get("previous"), kpi.search_count([]) - 1)
