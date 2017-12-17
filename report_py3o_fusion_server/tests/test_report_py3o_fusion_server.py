# -*- coding: utf-8 -*-
# Copyright 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import mock
from odoo.exceptions import ValidationError
from odoo.addons.report_py3o.tests import test_report_py3o


@mock.patch(
    'requests.post', mock.Mock(
        return_value=mock.Mock(
            status_code=200,
            iter_content=mock.Mock(return_value=['test_result']),
        )
    )
)
class TestReportPy3oFusionServer(test_report_py3o.TestReportPy3o):
    def setUp(self):
        super(TestReportPy3oFusionServer, self).setUp()
        py3o_server = self.env['py3o.server'].create({"url": "http://dummy"})
        # check the call to the fusion server
        self.report.write({
            "py3o_server_id": py3o_server.id,
            "py3o_filetype": 'pdf',
        })

    def test_no_local_fusion_without_fusion_server(self):
        self.assertTrue(self.report.py3o_is_local_fusion)
        with self.assertRaises(ValidationError) as e:
            self.report.write({"py3o_server_id": None})
        self.assertEqual(
            e.exception.name,
            "Can not use not native format in local fusion. "
            "Please specify a Fusion Server")

    def test_reports_no_local_fusion(self):
        self.report.py3o_is_local_fusion = False
        self.test_reports()
