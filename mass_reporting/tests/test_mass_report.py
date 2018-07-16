# -*- coding: utf-8 -*-
# Copyright 2018 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import base64
from StringIO import StringIO
import zipfile

from openerp.tests import common
from openerp.addons.connector.tests.common import mock_job_delay_to_direct


class TestMassReport(common.TransactionCase):
    """Test 'mass.report' data model."""

    def setUp(self):
        super(TestMassReport, self).setUp()
        model_partner = self.env['ir.model'].search(
            [('model', '=', 'res.partner')])
        report_partner_label = self.env.ref('base.res_partner_address_report')
        self.output_format_none = self.env['ir.model'].search(
            [('model', '=', 'mass.report.output.none')])
        self.output_format_concatenate = self.env['ir.model'].search(
            [('model', '=', 'mass.report.output.concatenate')])
        self.output_format_zip_files = self.env['ir.model'].search(
            [('model', '=', 'mass.report.output.zip_files')])
        vals = {
            'name': u"TEST res.partner labels",
            'model_id': model_partner.id,
            'user_id': self.env.user.id,
            'output_format': self.output_format_none.id,
            'line_ids': [
                (0, 0, {'report_id': report_partner_label.id}),
            ],
        }
        self.mr = self.env['mass.report'].create(vals)

    def _action_run(self):
        job1_path = ('openerp.addons.mass_reporting.models.mass_report.'
                     'run_main_job')
        job2_path = ('openerp.addons.mass_reporting.models.mass_report.'
                     'create_attachment')
        with mock_job_delay_to_direct(job1_path):
            with mock_job_delay_to_direct(job2_path):
                self.mr.action_run()
            self.assertTrue(self.mr.report_attachment_ids)
            for report_attachment in self.mr.report_attachment_ids:
                self.assertTrue(report_attachment.attachment_id)
                self.mr.action_build()

    def test_action_run_none(self):
        self.mr.output_format = self.output_format_none
        self._action_run()
        self.assertFalse(self.mr.output_file)

    def test_action_run_concatenate(self):
        self.mr.output_format = self.output_format_concatenate
        self._action_run()
        self.assertTrue(self.mr.output_file)

    def test_action_run_zip_files(self):
        self.mr.output_format = self.output_format_zip_files
        self._action_run()
        self.assertTrue(self.mr.output_file)

        content_b64 = self.mr.output_file.datas
        content = base64.decodestring(content_b64)
        file_ = StringIO(content)
        zip_file = zipfile.ZipFile(file_)
        self.assertIsNone(zip_file.testzip())
        zipped_files = zip_file.namelist()
        for ra in self.mr.report_attachment_ids:
            self.assertIn(ra.attachment_id.datas_fname, zipped_files)
