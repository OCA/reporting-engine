# -*- coding: utf-8 -*-
# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import csv
from StringIO import StringIO
from odoo.tests import common


class TestReport(common.TransactionCase):
    def setUp(self):
        super(TestReport, self,).setUp()
        self.Report = self.env['report']
        self.IrAttachment = self.env["ir.attachment"]
        self.csv_report = (
            self.env['report.report_csv.abstract']
            .with_context(active_model='res.partner')
        )
        self.report_name = 'report_csv.partner_csv'
        self.report = self.Report._get_report_from_name(self.report_name)
        self.docs = self.env['res.company'].search([], limit=1).partner_id

    def _get_doc_attachments(self, docs):
        return self.IrAttachment.search(
            [("res_id", "in", docs.ids),
             ("res_model", "=", docs._name)]
        )

    def test_report(self):
        report = self.report
        self.assertEqual(report.report_type, 'csv')
        rep = self.Report.get_csv(self.docs.ids, self.report_name, {})
        str_io = StringIO(rep[0])
        dict_report = list(csv.DictReader(str_io, delimiter=';',
                                          quoting=csv.QUOTE_ALL))
        self.assertEqual(self.docs.name, dict(dict_report[0])['name'])

    def test_report_save_in_attachment(self):
        attachment = self._get_doc_attachments(self.docs)
        self.report.attachment = "'test.csv'"
        self.report.attachment_use = True
        rep = self.Report.get_csv(self.docs.ids, self.report_name, {})
        attachment = self._get_doc_attachments(self.docs) - attachment
        self.assertTrue(attachment)
        self.assertEqual(attachment.datas.decode("base64"), rep[0])
        attachment.datas = "test".encode("base64")
        rep = self.Report.get_csv(self.docs.ids, self.report_name, {})
        self.assertEqual(rep[0], "test")

    def test_id_retrieval(self):

        # Typical call from WebUI with wizard
        objs = self.csv_report._get_objs_for_report(
            False, {"context": {"active_ids": self.docs.ids}})
        self.assertEquals(objs, self.docs)

        # Typical call from within code not to report_action
        objs = self.csv_report.with_context(
            active_ids=self.docs.ids)._get_objs_for_report(False, False)
        self.assertEquals(objs, self.docs)

        # Typical call from WebUI
        objs = self.csv_report._get_objs_for_report(
            self.docs.ids,
            {"data": [self.report_name, self.report.report_type]}
        )
        self.assertEquals(objs, self.docs)

        # Typical call from render
        objs = self.csv_report._get_objs_for_report(self.docs.ids, {})
        self.assertEquals(objs, self.docs)
