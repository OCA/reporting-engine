# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import odoo
from odoo.tools import mute_logger

from odoo.addons.web.tests.test_js import WebSuite


@odoo.tests.tagged("post_install", "-at_install")
class TestReportBuilderJS(WebSuite):
    """Test Report Builder JS code"""

    def get_hoot_filters(self):
        self._test_params = [("+", "@report_builder")]
        return super().get_hoot_filters()

    @mute_logger(
        "odoo.addons.report_builder.tests.test_js.TestReportBuilderJS.test_report_builder"
    )
    def test_report_builder(self):
        self.test_unit_desktop()
