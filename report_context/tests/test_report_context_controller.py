# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from unittest.mock import patch

from odoo.tests import HttpCase, tagged

from odoo.addons.base.models.ir_actions_report import IrActionsReport


@tagged("post_install", "-at_install")
class TestReportContextController(HttpCase):
    def test_report_route_uses_report_context(self):
        company = self.env.ref("base.main_company")
        report = self.env.ref("web.action_report_internalpreview")
        report.context = '{"test_parameter": 2}'
        seen = []
        orig = IrActionsReport._render_qweb_html

        def render(rep, *args, **kwargs):
            seen.append(rep.env.context.get("test_parameter"))
            return orig(rep, *args, **kwargs)

        self.authenticate("admin", "admin")
        with patch.object(IrActionsReport, "_render_qweb_html", render):
            res = self.url_open(f"/report/html/{report.report_name}/{company.id}")
        self.assertEqual(res.status_code, 200)
        self.assertIn(2, seen)
