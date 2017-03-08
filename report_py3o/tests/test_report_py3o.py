# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).).

from base64 import b64decode
import mock
import os
import pkg_resources
import shutil
import tempfile
from contextlib import contextmanager

from py3o.formats import Formats

from odoo import tools
from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError

from ..models.py3o_report import TemplateNotFound
from base64 import b64encode


@contextmanager
def temporary_copy(path):
    filname, ext = os.path.splitext(path)
    tmp_filename = tempfile.mktemp(suffix='.' + ext)
    try:
        shutil.copy2(path, tmp_filename)
        yield tmp_filename
    finally:
        os.unlink(tmp_filename)


class TestReportPy3o(TransactionCase):

    def setUp(self):
        super(TestReportPy3o, self).setUp()
        self.report = self.env.ref("report_py3o.res_users_report_py3o")
        self.py3o_report = self.env['py3o.report'].create({
            'ir_actions_report_xml_id': self.report.id})

    def test_no_local_fusion_without_fusion_server(self):
        self.assertTrue(self.report.py3o_is_local_fusion)
        with self.assertRaises(ValidationError) as e:
            self.report.py3o_is_local_fusion = False
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
        self.assertEqual(self.report.report_type, "py3o")
        with self.assertRaises(ValidationError) as e:
            self.report.py3o_filetype = False
        self.assertEqual(
            e.exception.name,
            "Field 'Output Format' is required for Py3O report")

    def test_reports(self):
        py3o_report = self.env['py3o.report']
        with mock.patch.object(
                py3o_report.__class__, '_create_single_report') as patched_pdf:
            result = tempfile.mktemp('.txt')
            with open(result, 'w') as fp:
                fp.write('dummy')
            patched_pdf.return_value = result
            # test the call the the create method inside our custom parser
            self.report.render_report(self.env.user.ids,
                                      self.report.report_name,
                                      {})
            self.assertEqual(1, patched_pdf.call_count)
            # generated files no more exists
            self.assertFalse(os.path.exists(result))
        res = self.report.render_report(
            self.env.user.ids, self.report.report_name, {})
        self.assertTrue(res)
        py3o_server = self.env['py3o.server'].create({"url": "http://dummy"})
        # check the call to the fusion server
        self.report.write({"py3o_filetype": "pdf",
                           "py3o_server_id": py3o_server.id})
        with mock.patch('requests.post') as patched_post:
            magick_response = mock.MagicMock()
            magick_response.status_code = 200
            patched_post.return_value = magick_response
            magick_response.iter_content.return_value = "test result"
            res = self.report.render_report(
                self.env.user.ids, self.report.report_name, {})
            self.assertEqual(('test result', 'pdf'), res)

    def test_report_post_process(self):
        """
        By default the post_process method is in charge to save the
        generated report into an ir.attachment if requested.
        """
        report = self.env.ref("report_py3o.res_users_report_py3o")
        report.attachment = "object.name + '.txt'"
        py3o_server = self.env['py3o.server'].create({"url": "http://dummy"})
        # check the call to the fusion server
        report.write({"py3o_filetype": "pdf",
                      "py3o_server_id": py3o_server.id})
        ir_attachment = self.env['ir.attachment']
        attachements = ir_attachment.search([(1, '=', 1)])
        with mock.patch('requests.post') as patched_post:
            magick_response = mock.MagicMock()
            magick_response.status_code = 200
            patched_post.return_value = magick_response
            magick_response.iter_content.return_value = "test result"
            res = report.render_report(
                self.env.user.ids, report.report_name, {})
            self.assertEqual(('test result', 'pdf'), res)
        attachements = ir_attachment.search([(1, '=', 1)]) - attachements
        self.assertEqual(1, len(attachements.ids))
        self.assertEqual(self.env.user.name + '.txt', attachements.name)
        self.assertEqual(self.env.user._name, attachements.res_model)
        self.assertEqual(self.env.user.id, attachements.res_id)
        self.assertEqual('test result', b64decode(attachements.datas))

    def test_report_template_configs(self):
        # the demo template is specified with a relative path in in the module
        # path
        tmpl_name = self.report.py3o_template_fallback
        flbk_filename = pkg_resources.resource_filename(
            "odoo.addons.%s" % self.report.module,
            tmpl_name)
        self.assertTrue(os.path.exists(flbk_filename))
        res = self.report.render_report(
            self.env.user.ids, self.report.report_name, {})
        self.assertTrue(res)
        # The generation fails if the tempalte is not found
        self.report.module = False
        with self.assertRaises(TemplateNotFound), self.env.cr.savepoint():
            self.report.render_report(
                self.env.user.ids, self.report.report_name, {})

        # the template can also be provided as an abspath if it's root path
        # is trusted
        self.report.py3o_template_fallback = flbk_filename
        with self.assertRaises(TemplateNotFound):
            self.report.render_report(
                self.env.user.ids, self.report.report_name, {})
        with temporary_copy(flbk_filename) as tmp_filename:
            self.report.py3o_template_fallback = tmp_filename
            tools.config.misc['report_py3o'] = {
                'root_tmpl_path': os.path.dirname(tmp_filename)}
            res = self.report.render_report(
                self.env.user.ids, self.report.report_name, {})
            self.assertTrue(res)

        # the tempalte can also be provided as a binay field
        self.report.py3o_template_fallback = False

        with open(flbk_filename) as tmpl_file:
            tmpl_data = b64encode(tmpl_file.read())
        py3o_template = self.env['py3o.template'].create({
            'name': 'test_template',
            'py3o_template_data': tmpl_data,
            'filetype': 'odt'})
        self.report.py3o_template_id = py3o_template
        self.report.py3o_template_fallback = flbk_filename
        res = self.report.render_report(
            self.env.user.ids, self.report.report_name, {})
        self.assertTrue(res)

    def test_report_template_fallback_validity(self):
        tmpl_name = self.report.py3o_template_fallback
        flbk_filename = pkg_resources.resource_filename(
            "odoo.addons.%s" % self.report.module,
            tmpl_name)
        # an exising file in a native format is a valid template if it's
        self.assertTrue(self.py3o_report._get_template_from_path(
            tmpl_name))
        self.report.module = None
        # a directory is not a valid template..
        self.assertFalse(self.py3o_report._get_template_from_path('/etc/'))
        self.assertFalse(self.py3o_report._get_template_from_path('.'))
        # an vaild template outside the root_tmpl_path is not a valid template
        # path
        # located in trusted directory
        self.report.py3o_template_fallback = flbk_filename
        self.assertFalse(self.py3o_report._get_template_from_path(
            flbk_filename))
        with temporary_copy(flbk_filename) as tmp_filename:
            self.assertTrue(self.py3o_report._get_template_from_path(
                tmp_filename))
        # check security
        self.assertFalse(self.py3o_report._get_template_from_path(
            'rm -rf . & %s' % flbk_filename))
        # a file in a non native LibreOffice format is not a valid template
        with tempfile.NamedTemporaryFile(suffix='.toto')as f:
            self.assertFalse(self.py3o_report._get_template_from_path(
                f.name))
        # non exising files are not valid template
        self.assertFalse(self.py3o_report._get_template_from_path(
            '/etc/test.odt'))
