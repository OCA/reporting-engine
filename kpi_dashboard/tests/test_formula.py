# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError


class TestFormula(TransactionCase):
    def setUp(self):
        super().setUp()
        self.kpi = self.env["kpi.kpi"].create(
            {
                "name": "DEMO KPI",
                "widget": "number",
                "computation_method": "code",
            }
        )

    def test_forbidden_words_01(self):
        self.kpi.code = """
result = {"value": 0}
self.env.cr.commit()
"""
        with self.assertRaises(ValidationError):
            self.kpi.compute()

    def test_forbidden_words_02(self):
        self.kpi.code = """
result = {"value": 0}
self.env.cr.rollback()
"""
        with self.assertRaises(ValidationError):
            self.kpi.compute()

    def test_forbidden_words_03(self):
        self.kpi.code = """
result = {"value": 0}
self.env.cr.execute("CoMMiT")
"""
        with self.assertRaises(ValidationError):
            self.kpi.compute()

    def test_computation(self):
        self.assertFalse(self.kpi.value)
        self.kpi.compute()
        self.assertEqual(self.kpi.value, {})
        self.kpi.code = """
result = {}
result['value'] = len(model.search([('id', '=', %s)]))
result['previous'] = len(model.search([('id', '!=', %s)]))
        """ % (
            self.kpi.id,
            self.kpi.id,
        )
        self.kpi.compute()
        value = self.kpi.value
        self.assertTrue(value.get("value"))
        self.assertEqual(value.get("value"), 1)
        self.assertEqual(value.get("previous"), self.kpi.search_count([]) - 1)
        self.assertFalse(self.kpi.history_ids)

    def test_computation_history(self):
        self.assertFalse(self.kpi.value)
        self.kpi.store_history = True
        self.kpi.compute()
        self.assertTrue(self.kpi.history_ids)
        self.assertEqual(self.kpi.value, {})
        self.kpi.code = """
result = {}
result['value'] = len(model.search([('id', '=', %s)]))
result['previous'] = len(model.search([('id', '!=', %s)]))
        """ % (
            self.kpi.id,
            self.kpi.id,
        )
        self.kpi.compute()
        value = self.kpi.value
        self.assertTrue(value.get("value"))
        self.assertEqual(value.get("value"), 1)
        self.assertEqual(value.get("previous"), self.kpi.search_count([]) - 1)
        self.assertTrue(self.kpi.history_ids)
