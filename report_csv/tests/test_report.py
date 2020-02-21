# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging
from io import StringIO

from odoo.tests import common

_logger = logging.getLogger(__name__)
try:
    import csv
except ImportError:
    _logger.debug("Can not import csv.")


class TestReport(common.TransactionCase):
    def setUp(self):
        super().setUp()
        report_object = self.env["ir.actions.report"]
        self.csv_report = self.env["report.report_csv.abstract"].with_context(
            active_model="res.partner"
        )
        self.report_name = "report_csv.partner_csv"
        self.report = report_object._get_report_from_name(self.report_name)
        self.docs = self.env["res.company"].search([], limit=1).partner_id

    def test_report(self):
        # Test if not res:
        self.env["ir.actions.report"]._get_report_from_name("TEST")
        report = self.report
        self.assertEqual(report.report_type, "csv")
        rep = report.render(self.docs.ids, {})
        str_io = StringIO(rep[0])
        dict_report = list(csv.DictReader(str_io, delimiter=";", quoting=csv.QUOTE_ALL))
        self.assertEqual(self.docs.name, dict(dict_report[0])["name"])

    def test_id_retrieval(self):

        # Typical call from WebUI with wizard
        objs = self.csv_report._get_objs_for_report(
            False, {"context": {"active_ids": self.docs.ids}}
        )
        self.assertEquals(objs, self.docs)

        # Typical call from within code not to report_action
        objs = self.csv_report.with_context(
            active_ids=self.docs.ids
        )._get_objs_for_report(False, False)
        self.assertEquals(objs, self.docs)

        # Typical call from WebUI
        objs = self.csv_report._get_objs_for_report(
            self.docs.ids, {"data": [self.report_name, self.report.report_type]}
        )
        self.assertEquals(objs, self.docs)

        # Typical call from render
        objs = self.csv_report._get_objs_for_report(self.docs.ids, {})
        self.assertEquals(objs, self.docs)
