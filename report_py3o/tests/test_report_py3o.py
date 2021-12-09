# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).).

import base64
import logging
import os
import shutil
import tempfile
from base64 import b64decode, b64encode
from contextlib import contextmanager
from unittest import mock

import pkg_resources
from PyPDF2 import PdfFileWriter
from PyPDF2.pdf import PageObject

from odoo import tools
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from odoo.addons.base.tests.test_mimetypes import PNG

from ..models._py3o_parser_context import format_multiline_value
from ..models.ir_actions_report import PY3O_CONVERSION_COMMAND_PARAMETER
from ..models.py3o_report import TemplateNotFound

logger = logging.getLogger(__name__)

try:
    from genshi.core import Markup
except ImportError:
    logger.debug("Cannot import genshi.core")


@contextmanager
def temporary_copy(path):
    filname, ext = os.path.splitext(path)
    tmp_filename = tempfile.mktemp(suffix="." + ext)
    try:
        shutil.copy2(path, tmp_filename)
        yield tmp_filename
    finally:
        os.unlink(tmp_filename)


class TestReportPy3o(TransactionCase):
    def setUp(self):
        super(TestReportPy3o, self).setUp()
        self.env.user.image_1920 = PNG
        self.report = self.env.ref("report_py3o.res_users_report_py3o")
        self.py3o_report = self.env["py3o.report"].create(
            {"ir_actions_report_id": self.report.id}
        )

    def test_required_py3_filetype(self):
        self.assertEqual(self.report.report_type, "py3o")
        with self.assertRaises(ValidationError) as e:
            self.report.py3o_filetype = False
        self.assertEqual(
            e.exception.args[0], "Field 'Output Format' is required for Py3O report"
        )

    def _render_patched(self, result_text="test result", call_count=1):
        py3o_report = self.env["py3o.report"]
        py3o_report_obj = py3o_report.create({"ir_actions_report_id": self.report.id})
        with mock.patch.object(
            py3o_report.__class__, "_create_single_report"
        ) as patched_pdf:
            result = tempfile.mktemp(".txt")
            with open(result, "w") as fp:
                fp.write(result_text)
            patched_pdf.side_effect = (
                lambda record, data: py3o_report_obj._postprocess_report(record, result)
                or result
            )
            # test the call the the create method inside our custom parser
            self.report._render(self.env.user.ids)
            self.assertEqual(call_count, patched_pdf.call_count)
            # generated files no more exists
            self.assertFalse(os.path.exists(result))

    def test_reports(self):
        res = self.report._render(self.env.user.ids)
        self.assertTrue(res)

    def test_reports_merge_zip(self):
        self.report.py3o_filetype = "odt"
        users = self.env["res.users"].search([])
        self.assertTrue(len(users) > 0)
        py3o_report = self.env["py3o.report"]
        _zip_results = self.py3o_report._zip_results
        with mock.patch.object(
            py3o_report.__class__, "_zip_results"
        ) as patched_zip_results:
            patched_zip_results.side_effect = _zip_results
            content, filetype = self.report._render(users.ids)
            self.assertEqual(1, patched_zip_results.call_count)
            self.assertEqual(filetype, "zip")

    def test_reports_merge_pdf(self):
        reports_path = []
        for _i in range(0, 3):
            result = tempfile.mktemp(".txt")
            writer = PdfFileWriter()
            writer.addPage(PageObject.createBlankPage(width=100, height=100))
            with open(result, "wb") as fp:
                writer.write(fp)
            reports_path.append(result)
        res = self.py3o_report._merge_pdf(reports_path)
        self.assertTrue(res)

    def test_report_load_from_attachment(self):
        self.report.write({"attachment_use": True, "attachment": "'my_saved_report'"})
        attachments = self.env["ir.attachment"].search([])
        self._render_patched()
        new_attachments = self.env["ir.attachment"].search([])
        created_attachement = new_attachments - attachments
        self.assertEqual(1, len(created_attachement))
        content = b64decode(created_attachement.datas)
        self.assertEqual(b"test result", content)
        # put a new content into tha attachement and check that the next
        # time we ask the report we received the saved attachment not a newly
        # generated document
        created_attachement.datas = base64.b64encode(b"new content")
        res = self.report._render(self.env.user.ids)
        self.assertEqual((b"new content", self.report.py3o_filetype), res)

    def test_report_post_process(self):
        """
        By default the post_process method is in charge to save the
        generated report into an ir.attachment if requested.
        """
        self.report.attachment = "object.name + '.txt'"
        ir_attachment = self.env["ir.attachment"]
        attachements = ir_attachment.search([(1, "=", 1)])
        self._render_patched()
        attachements = ir_attachment.search([(1, "=", 1)]) - attachements
        self.assertEqual(1, len(attachements.ids))
        self.assertEqual(self.env.user.name + ".txt", attachements.name)
        self.assertEqual(self.env.user._name, attachements.res_model)
        self.assertEqual(self.env.user.id, attachements.res_id)
        self.assertEqual(b"test result", b64decode(attachements.datas))

    @tools.misc.mute_logger("odoo.addons.report_py3o.models.py3o_report")
    def test_report_template_configs(self):
        # the demo template is specified with a relative path in in the module
        # path
        tmpl_name = self.report.py3o_template_fallback
        flbk_filename = pkg_resources.resource_filename(
            "odoo.addons.%s" % self.report.module, tmpl_name
        )
        self.assertTrue(os.path.exists(flbk_filename))
        res = self.report._render(self.env.user.ids)
        self.assertTrue(res)
        # The generation fails if the template is not found
        self.report.module = False
        with self.assertRaises(TemplateNotFound), self.env.cr.savepoint():
            self.report._render(self.env.user.ids)

        # the template can also be provided as an abspath if it's root path
        # is trusted
        self.report.py3o_template_fallback = flbk_filename
        with self.assertRaises(TemplateNotFound):
            self.report._render(self.env.user.ids)
        with temporary_copy(flbk_filename) as tmp_filename:
            self.report.py3o_template_fallback = tmp_filename
            tools.config.misc["report_py3o"] = {
                "root_tmpl_path": os.path.dirname(tmp_filename)
            }
            res = self.report._render(self.env.user.ids)
            self.assertTrue(res)

        # the tempalte can also be provided as a binary field
        self.report.py3o_template_fallback = False

        with open(flbk_filename, "rb") as tmpl_file:
            tmpl_data = b64encode(tmpl_file.read())
        py3o_template = self.env["py3o.template"].create(
            {
                "name": "test_template",
                "py3o_template_data": tmpl_data,
                "filetype": "odt",
            }
        )
        self.report.py3o_template_id = py3o_template
        self.report.py3o_template_fallback = flbk_filename
        res = self.report._render(self.env.user.ids)
        self.assertTrue(res)

    @tools.misc.mute_logger("odoo.addons.report_py3o.models.py3o_report")
    def test_report_template_fallback_validity(self):
        tmpl_name = self.report.py3o_template_fallback
        flbk_filename = pkg_resources.resource_filename(
            "odoo.addons.%s" % self.report.module, tmpl_name
        )
        # an exising file in a native format is a valid template if it's
        self.assertTrue(self.py3o_report._get_template_from_path(tmpl_name))
        self.report.module = None
        # a directory is not a valid template..
        self.assertFalse(self.py3o_report._get_template_from_path("/etc/"))
        self.assertFalse(self.py3o_report._get_template_from_path("."))
        # an vaild template outside the root_tmpl_path is not a valid template
        # path
        # located in trusted directory
        self.report.py3o_template_fallback = flbk_filename
        self.assertFalse(self.py3o_report._get_template_from_path(flbk_filename))
        with temporary_copy(flbk_filename) as tmp_filename:
            self.assertTrue(self.py3o_report._get_template_from_path(tmp_filename))
        # check security
        self.assertFalse(
            self.py3o_report._get_template_from_path("rm -rf . & %s" % flbk_filename)
        )
        # a file in a non native LibreOffice format is not a valid template
        with tempfile.NamedTemporaryFile(suffix=".toto") as f:
            self.assertFalse(self.py3o_report._get_template_from_path(f.name))
        # non exising files are not valid template
        self.assertFalse(self.py3o_report._get_template_from_path("/etc/test.odt"))

    def test_escape_html_characters_format_multiline_value(self):
        self.assertEqual(
            Markup("&lt;&gt;<text:line-break/>&amp;test;"),
            format_multiline_value("<>\n&test;"),
        )

    def test_py3o_report_availability(self):
        # This test could fails if libreoffice is not available on the server
        self.report.py3o_filetype = "odt"
        self.assertTrue(self.report.lo_bin_path)
        self.assertTrue(self.report.is_py3o_native_format)
        self.assertFalse(self.report.is_py3o_report_not_available)
        self.assertFalse(self.report.msg_py3o_report_not_available)

        # specify a wrong lo bin path
        self.env["ir.config_parameter"].set_param(
            PY3O_CONVERSION_COMMAND_PARAMETER, "/wrong_path"
        )
        self.report.refresh()
        # no bin path available but the report is still available since
        # the output is into native format
        self.assertFalse(self.report.lo_bin_path)
        self.assertFalse(self.report.is_py3o_report_not_available)
        self.assertFalse(self.report.msg_py3o_report_not_available)
        res = self.report._render(self.env.user.ids)
        self.assertTrue(res)

        # The report should become unavailable for an non native output format
        self.report.py3o_filetype = "pdf"
        self.assertFalse(self.report.is_py3o_native_format)
        self.assertTrue(self.report.is_py3o_report_not_available)
        self.assertTrue(self.report.msg_py3o_report_not_available)
        with self.assertRaises(RuntimeError):
            self.report._render(self.env.user.ids)

        # if we reset the wrong path, everything should work
        self.env["ir.config_parameter"].set_param(
            PY3O_CONVERSION_COMMAND_PARAMETER, "libreoffice"
        )
        self.report.refresh()
        self.assertTrue(self.report.lo_bin_path)
        self.assertFalse(self.report.is_py3o_native_format)
        self.assertFalse(self.report.is_py3o_report_not_available)
        self.assertFalse(self.report.msg_py3o_report_not_available)
        res = self.report._render(self.env.user.ids)
        self.assertTrue(res)
