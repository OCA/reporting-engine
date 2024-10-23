# Copyright 2024 Hunki Enterprises BV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl-3.0)

from odoo.tests.common import tagged

from odoo.addons.sql_export.tests import test_sql_query

from ..hooks import uninstall_hook


@tagged("post_install", "-at_install")
class TestSqlExportDelta(test_sql_query.TestExportSqlQuery):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sql_report_demo.export_delta = True

    def test_sql_query(self):
        """Test that exporting demo report twice exports empty delta"""
        result = super().test_sql_query()
        with self.assertRaises(AssertionError):
            super().test_sql_query()
        self.assertTrue(self.sql_report_demo._export_delta_existing_tables())
        uninstall_hook(self.env.cr, self.env.registry)
        self.assertFalse(self.sql_report_demo._export_delta_existing_tables())
        return result
