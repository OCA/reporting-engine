# Copyright 2026 Camptocamp
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo.tests import tagged
from odoo.tests.common import SingleTransactionCase


@tagged("-at_install", "post_install")
class TestIrModel(SingleTransactionCase):
    """OCA/reporting-engine#1120: bi_sql_editor view models should not spam
    the log with "disabling automatic schema management" on every registry
    reload, since being backed by a view is expected for them.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        view = cls.env.ref("bi_sql_editor.partner_sql_view")
        cls.view = view.copy(default={"technical_name": "test_ir_model_logging"})
        cls.view.button_validate_sql_expression()
        cls.view.button_create_sql_view_and_model()

    def test_no_schema_management_log_for_bi_sql_view_model(self):
        logger = logging.getLogger("odoo.addons.base.models.ir_model")
        with self.assertNoLogs(logger, level="INFO"):
            self.env["ir.model"]._add_manual_models()

        model = self.env[self.view.model_name]
        self.assertFalse(model._auto)
