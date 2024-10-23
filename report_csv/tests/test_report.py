# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import json
import logging
from io import StringIO
from unittest import mock

from odoo import http
from odoo.exceptions import UserError
from odoo.tests import common
from odoo.tools import mute_logger

from odoo.addons.web.controllers.report import ReportController

_logger = logging.getLogger(__name__)
try:
    import csv
except ImportError:
    _logger.debug("Can not import csv.")


class TestCsvException(Exception):
    def __init__(self, message):
        """
        :param message: exception message and frontend modal content
        """
        super().__init__(message)


class TestReport(common.TransactionCase):
    def setUp(self):
        super().setUp()
        self.report_object = self.env["ir.actions.report"]
        self.csv_report = self.env["report.report_csv.abstract"].with_context(
            active_model="res.partner"
        )
        self.report_name = "report_csv.partner_csv"
        self.report = self.report_object._get_report_from_name(self.report_name)
        self.docs = self.env["res.company"].search([], limit=1).partner_id

    def test_report(self):
        # Test if not res:
        report = self.report
        self.assertEqual(report.report_type, "csv")
        rep = self.report_object._render(self.report_name, self.docs.ids, {})
        str_io = StringIO(rep[0])
        dict_report = list(csv.DictReader(str_io, delimiter=";", quoting=csv.QUOTE_ALL))
        self.assertEqual(self.docs.name, dict(dict_report[0])["name"])

    def test_id_retrieval(self):
        # Typical call from WebUI with wizard
        objs = self.csv_report._get_objs_for_report(
            False, {"context": {"active_ids": self.docs.ids}}
        )
        self.assertEqual(objs, self.docs)

        # Typical call from within code not to report_action
        objs = self.csv_report.with_context(
            active_ids=self.docs.ids
        )._get_objs_for_report(False, False)
        self.assertEqual(objs, self.docs)

        # Typical call from WebUI
        objs = self.csv_report._get_objs_for_report(
            self.docs.ids, {"data": [self.report_name, self.report.report_type]}
        )
        self.assertEqual(objs, self.docs)

        # Typical call from render
        objs = self.csv_report._get_objs_for_report(self.docs.ids, {})
        self.assertEqual(objs, self.docs)

    def test_report_with_encoding(self):
        report = self.report
        report.write({"encoding": "cp932"})
        rep = report._render_csv(self.report_name, self.docs.ids, {})
        str_io = StringIO(rep[0].decode())
        dict_report = list(csv.DictReader(str_io, delimiter=";", quoting=csv.QUOTE_ALL))
        self.assertEqual(self.docs.name, dict(dict_report[0])["name"])

        report.write({"encoding": "xyz"})
        with self.assertRaises(UserError):
            rep = report._render_csv(self.report_name, self.docs.ids, {})


class TestCsvReport(common.HttpCase):
    """
    Some tests calling controller
    """

    def setUp(self):
        super().setUp()
        self.report_object = self.env["ir.actions.report"]
        self.csv_report = self.env["report.report_csv.abstract"].with_context(
            active_model="res.partner"
        )
        self.report_name = "report_csv.partner_csv"
        self.report = self.report_object._get_report_from_name(self.report_name)
        self.docs = self.env["res.company"].search([], limit=1).partner_id
        self.session = self.authenticate("admin", "admin")

    def test_csv(self):
        filename = self.get_report_headers().headers.get("Content-Disposition")
        self.assertTrue(".csv" in filename)

    @mute_logger("odoo.addons.web.controllers.report")
    def test_pdf_error(self):
        with mock.patch.object(
            ReportController, "report_routes"
        ) as route_patch, self.assertLogs(
            "odoo.addons.report_csv.controllers.main", level=logging.ERROR
        ) as cm:
            route_patch.side_effect = TestCsvException("Test")
            self.get_report_headers(
                suffix="/report/pdf/test/10", f_type="qweb-pdf"
            ).headers.get("Content-Disposition")
            [msg] = cm.output
            self.assertIn("Error while generating report", msg)

    def get_report_headers(
        self, suffix="/report/csv/report_csv.partner_csv/1", f_type="csv"
    ):
        return self.url_open(
            url="/report/download",
            data={
                "data": json.dumps([suffix, f_type]),
                "csrf_token": http.Request.csrf_token(self),
            },
        )
