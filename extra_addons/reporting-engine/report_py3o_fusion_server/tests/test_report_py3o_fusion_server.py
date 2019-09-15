# Copyright 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import mock
from odoo.exceptions import ValidationError
from odoo.addons.report_py3o.models.ir_actions_report import \
    PY3O_CONVERSION_COMMAND_PARAMETER
from odoo.addons.report_py3o.tests import test_report_py3o


@mock.patch(
    'requests.post', mock.Mock(
        return_value=mock.Mock(
            status_code=200,
            iter_content=mock.Mock(return_value=[b'test_result']),
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
        self.py3o_server = py3o_server

    def test_no_local_fusion_without_fusion_server(self):
        self.assertTrue(self.report.py3o_is_local_fusion)
        # Fusion server is only required if not local...
        self.report.write({
            "py3o_server_id": None,
            "py3o_is_local_fusion": True,
            })
        self.report.write({
            "py3o_server_id": self.py3o_server.id,
            "py3o_is_local_fusion": True,
            })
        self.report.write({
            "py3o_server_id": self.py3o_server.id,
            "py3o_is_local_fusion": False,
            })
        with self.assertRaises(ValidationError) as e:
            self.report.write({
                "py3o_server_id": None,
                "py3o_is_local_fusion": False,
                })
        self.assertEqual(
            e.exception.name,
            "You can not use remote fusion without Fusion server. "
            "Please specify a Fusion Server")

    def test_reports_no_local_fusion(self):
        self.report.py3o_is_local_fusion = False
        self.test_reports()

    def test_odoo2libreoffice_options(self):
        for options in self.env['py3o.pdf.options'].search([]):
            options_dict = options.odoo2libreoffice_options()
            self.assertIsInstance(options_dict, dict)

    def test_py3o_report_availability(self):
        # if the report is not into a native format, we must have at least
        # a libreoffice runtime or a fusion server. Otherwise the report is
        # not usable and will fail at rutime.
        # This test could fails if libreoffice is not available on the server
        self.report.py3o_filetype = "odt"
        self.assertTrue(self.report.lo_bin_path)
        self.assertTrue(self.report.py3o_server_id)
        self.assertTrue(self.report.is_py3o_native_format)
        self.assertFalse(self.report.is_py3o_report_not_available)
        self.assertFalse(self.report.msg_py3o_report_not_available)

        # specify a wrong lo bin path and a non native format.
        self.env['ir.config_parameter'].set_param(
            PY3O_CONVERSION_COMMAND_PARAMETER, "/wrong_path")
        self.report.py3o_filetype = "pdf"
        self.report.refresh()
        # no native and no bin path, everything is still OK since a fusion
        # server is specified.
        self.assertFalse(self.report.lo_bin_path)
        self.assertTrue(self.report.py3o_server_id)
        self.assertFalse(self.report.is_py3o_native_format)
        self.assertFalse(self.report.is_py3o_report_not_available)
        self.assertFalse(self.report.msg_py3o_report_not_available)

        # if we remove the fusion server, the report becomes unavailable
        self.report.py3o_server_id = False
        self.assertTrue(self.report.is_py3o_report_not_available)
        self.assertTrue(self.report.msg_py3o_report_not_available)

        # if we set a libreffice runtime, the report is available again
        self.env['ir.config_parameter'].set_param(
            PY3O_CONVERSION_COMMAND_PARAMETER, "libreoffice")
        self.report.refresh()
        self.assertTrue(self.report.lo_bin_path)
        self.assertFalse(self.report.is_py3o_report_not_available)
        self.assertFalse(self.report.msg_py3o_report_not_available)
