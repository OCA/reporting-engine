# Copyright 2017 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from requests.exceptions import HTTPError

from odoo.tests import common


@common.tagged("-at_install", "post_install")
class TestReport(common.HttpCase):
    def setUp(self):
        super(TestReport, self).setUp()
        self.user = self.env["res.users"].create(
            {
                "name": "DEMO USER",
                "login": "test_demo_user",
                "password": "test_demo_user",
                "groups_id": [(4, self.env.ref("base.group_user").id)],
            }
        )

    def test_web_report(self):
        self.authenticate(self.user.login, self.user.login)
        docs = self.env["res.company"].search([], limit=1).partner_id
        data = self.url_open(
            "/report/external_pdf/report_external_pdf.company_external_pdf/%s" % docs.id
        )
        data.raise_for_status()
        self.assertEqual(data.status_code, 200)

    def test_web_report_error(self):
        self.authenticate(self.user.login, self.user.login)
        docs = self.env["res.company"].search([], limit=1).partner_id
        data = self.url_open(
            "/report/external_pdf/report_external_pdf.no_company_external_pdf/%s"
            % docs.id
        )
        with self.assertRaises(HTTPError):
            data.raise_for_status()
