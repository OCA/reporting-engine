# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).).

import mock
import os
import pkg_resources
import tempfile

from py3o.formats import Formats

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

from ..models.py3o_report import TemplateNotFound
from base64 import b64encode


class TestReportPy3o(TransactionCase):

    def test_no_local_fusion_without_fusion_server(self):
        report = self.env.ref("report_py3o.res_users_report_py3o")
        self.assertTrue(report.py3o_is_local_fusion)
        with self.assertRaises(ValidationError) as e:
            report.py3o_is_local_fusion = False
        self.assertEqual(
            e.exception.name,
            "Can not use not native format in local fusion. "
            "Please specify a Fusion Server")

    def test_no_native_format_without_fusion_server(self):
        report = self.env.ref("report_py3o.res_users_report_py3o")
        formats = Formats()
        is_native = formats.get_format(report.py3o_filetype).native
        self.assertTrue(is_native)
        new_format = None
        for name in formats.get_known_format_names():
            format = formats.get_format(name)
            if not format.native:
                new_format = name
                break
        self.assertTrue(new_format)
        with self.assertRaises(ValidationError) as e:
            report.py3o_filetype = new_format
        self.assertEqual(
            e.exception.name,
            "Can not use not native format in local fusion. "
            "Please specify a Fusion Server")

    def test_required_py3_filetype(self):
        report = self.env.ref("report_py3o.res_users_report_py3o")
        self.assertEqual(report.report_type, "py3o")
        with self.assertRaises(ValidationError) as e:
            report.py3o_filetype = False
        self.assertEqual(
            e.exception.name,
            "Field 'Output Format' is required for Py3O report")

    def test_reports(self):
        py3o_report = self.env['py3o.report']
        report = self.env.ref("report_py3o.res_users_report_py3o")
        with mock.patch.object(
                py3o_report.__class__, '_create_single_report') as patched_pdf:
            result = tempfile.mktemp('.txt')
            with open(result, 'w') as fp:
                fp.write('dummy')
            patched_pdf.return_value = result
            # test the call the the create method inside our custom parser
            report.render_report(self.env.user.ids,
                                 report.report_name,
                                 {})
            self.assertEqual(1, patched_pdf.call_count)
            # generated files no more exists
            self.assertFalse(os.path.exists(result))
        res = report.render_report(
            self.env.user.ids, report.report_name, {})
        self.assertTrue(res)
        py3o_server = self.env['py3o.server'].create({"url": "http://dummy"})
        # check the call to the fusion server
        report.write({"py3o_filetype": "pdf",
                      "py3o_server_id": py3o_server.id})
        with mock.patch('requests.post') as patched_post:
            magick_response = mock.MagicMock()
            magick_response.status_code = 200
            patched_post.return_value = magick_response
            magick_response.iter_content.return_value = "test result"
            res = report.render_report(
                self.env.user.ids, report.report_name, {})
            self.assertEqual(('test result', 'pdf'), res)

    def test_report_template_configs(self):
        report = self.env.ref("report_py3o.res_users_report_py3o")
        # the demo template is specified with a relative path in in the module
        # path
        tmpl_name = report.py3o_template_fallback
        flbk_filename = pkg_resources.resource_filename(
            "odoo.addons.%s" % report.module,
            tmpl_name)
        self.assertTrue(os.path.exists(flbk_filename))
        res = report.render_report(
            self.env.user.ids, report.report_name, {})
        self.assertTrue(res)
        # The generation fails if the tempalte is not found
        report.module = False
        with self.assertRaises(TemplateNotFound), self.env.cr.savepoint():
            report.render_report(
                self.env.user.ids, report.report_name, {})

        # the template can also be provided as an abspaath
        report.py3o_template_fallback = flbk_filename
        res = report.render_report(
            self.env.user.ids, report.report_name, {})
        self.assertTrue(res)

        # the tempalte can also be provided as a binay field
        report.py3o_template_fallback = False

        with open(flbk_filename) as tmpl_file:
            tmpl_data = b64encode(tmpl_file.read())
        py3o_template = self.env['py3o.template'].create({
            'name': 'test_template',
            'py3o_template_data': tmpl_data,
            'filetype': 'odt'})
        report.py3o_template_id = py3o_template
        report.py3o_template_fallback = flbk_filename
        res = report.render_report(
            self.env.user.ids, report.report_name, {})
        self.assertTrue(res)
