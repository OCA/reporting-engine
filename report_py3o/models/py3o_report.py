# Copyright 2013 XCG Consulting (http://odoo.consulting)
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import base64
import logging
import os
import subprocess
import sys
import tempfile
import warnings
from base64 import b64decode
from contextlib import closing
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

import pkg_resources

from odoo import _, api, fields, models, tools

from ._py3o_parser_context import Py3oParserContext

logger = logging.getLogger(__name__)

try:
    # workaround for https://github.com/edgewall/genshi/issues/15
    # that makes runbot build red because of the DeprecationWarning
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        from py3o.template import Template
    from py3o import formats
except ImportError:
    logger.debug("Cannot import py3o.template")
try:
    from py3o.formats import Formats, UnkownFormatException
except ImportError:
    logger.debug("Cannot import py3o.formats")
try:
    from PyPDF2 import PdfFileReader, PdfFileWriter
except ImportError:
    logger.debug("Cannot import PyPDF2")

_extender_functions = {}


class TemplateNotFound(Exception):
    pass


def py3o_report_extender(report_xml_id=None):
    """
    A decorator to define function to extend the context sent to a template.
    This will be called at the creation of the report.
    The following arguments will be passed to it:
        - ir_report: report instance
        - localcontext: The context that will be passed to the report engine
    If no report_xml_id is given the extender is registered for all py3o
    reports
    Idea copied from CampToCamp report_webkit module.

    :param report_xml_id: xml id of the report
    :return: a decorated class
    """
    global _extender_functions

    def fct1(fct):
        _extender_functions.setdefault(report_xml_id, []).append(fct)
        return fct

    return fct1


@py3o_report_extender()
def default_extend(report_xml, context):
    context["report_xml"] = report_xml


class Py3oReport(models.TransientModel):
    _name = "py3o.report"
    _description = "Report Py30"

    ir_actions_report_id = fields.Many2one(
        comodel_name="ir.actions.report", required=True
    )

    def _is_valid_template_path(self, path):
        """Check if the path is a trusted path for py3o templates."""
        real_path = os.path.realpath(path)
        root_path = tools.config.get_misc("report_py3o", "root_tmpl_path")
        if not root_path:
            logger.warning(
                "You must provide a root template path into odoo.cfg to be "
                "able to use py3o template configured with an absolute path "
                "%s",
                real_path,
            )
            return False
        is_valid = real_path.startswith(root_path + os.path.sep)
        if not is_valid:
            logger.warning(
                "Py3o template path is not valid. %s is not a child of root " "path %s",
                real_path,
                root_path,
            )
        return is_valid

    def _is_valid_template_filename(self, filename):
        """Check if the filename can be used as py3o template"""
        if filename and os.path.isfile(filename):
            fname, ext = os.path.splitext(filename)
            ext = ext.replace(".", "")
            try:
                fformat = Formats().get_format(ext)
                if fformat and fformat.native:
                    return True
            except UnkownFormatException:
                logger.warning("Invalid py3o template %s", filename, exc_info=1)
        logger.warning("%s is not a valid Py3o template filename", filename)
        return False

    def _get_template_from_path(self, tmpl_name):
        """Return the template from the path to root of the module if specied
        or an absolute path on your server
        """
        if not tmpl_name:
            return None
        report_xml = self.ir_actions_report_id
        flbk_filename = None
        if report_xml.module:
            # if the default is defined
            flbk_filename = pkg_resources.resource_filename(
                "odoo.addons.%s" % report_xml.module, tmpl_name
            )
        elif self._is_valid_template_path(tmpl_name):
            flbk_filename = os.path.realpath(tmpl_name)
        if self._is_valid_template_filename(flbk_filename):
            with open(flbk_filename, "rb") as tmpl:
                return tmpl.read()
        return None

    def _get_template_fallback(self, model_instance):
        """
        Return the template referenced in the report definition
        :return:
        """
        self.ensure_one()
        report_xml = self.ir_actions_report_id
        return self._get_template_from_path(report_xml.py3o_template_fallback)

    def get_template(self, model_instance):
        """private helper to fetch the template data either from the database
        or from the default template file provided by the implementer.

        ATM this method takes a report definition recordset
        to try and fetch the report template from database. If not found it
        will fallback to the template file referenced in the report definition.

        @returns: string or buffer containing the template data

        @raises: TemplateNotFound which is a subclass of
        odoo.exceptions.DeferredException
        """
        self.ensure_one()
        report_xml = self.ir_actions_report_id
        if report_xml.py3o_template_id.py3o_template_data:
            # if a user gave a report template
            tmpl_data = b64decode(report_xml.py3o_template_id.py3o_template_data)

        else:
            tmpl_data = self._get_template_fallback(model_instance)

        if tmpl_data is None:
            # if for any reason the template is not found
            raise TemplateNotFound(_("No template found. Aborting."), sys.exc_info())

        return tmpl_data

    def _extend_parser_context(self, context, report_xml):
        # add default extenders
        for fct in _extender_functions.get(None, []):
            fct(report_xml, context)
        # add extenders for registered on the template
        xml_id = report_xml.get_external_id().get(report_xml.id)
        if xml_id in _extender_functions:
            for fct in _extender_functions[xml_id]:
                fct(report_xml, context)

    def _get_parser_context(self, model_instance, data):
        report_xml = self.ir_actions_report_id
        context = Py3oParserContext(self.env).localcontext
        context.update(report_xml._get_rendering_context(model_instance.ids, data))
        context["objects"] = model_instance
        self._extend_parser_context(context, report_xml)
        return context

    def _postprocess_report(self, model_instance, result_path):
        if len(model_instance) == 1 and self.ir_actions_report_id.attachment:
            with open(result_path, "rb") as f:
                # we do all the generation process using files to avoid memory
                # consumption...
                # ... but odoo wants the whole data in memory anyways :)
                buffer = BytesIO(f.read())
                self.ir_actions_report_id._postprocess_pdf_report(
                    model_instance, buffer
                )
        return result_path

    def _create_single_report(self, model_instance, data):
        """This function to generate our py3o report"""
        self.ensure_one()
        action_report = self.ir_actions_report_id
        filetype = action_report.py3o_filetype
        if filetype not in ("odt", "ods", "odp", "fodt", "fods", "fodp"):
            filetype = "ods"
        result_fd, result_path = tempfile.mkstemp(
            suffix="." + filetype, prefix="p3o.report.tmp."
        )
        tmpl_data = self.get_template(model_instance)

        in_stream = BytesIO(tmpl_data)
        with closing(os.fdopen(result_fd, "wb+")) as out_stream:
            template = Template(in_stream, out_stream, escape_false=True)
            localcontext = self._get_parser_context(model_instance, data)
            template.render(localcontext)
            out_stream.seek(0)
            tmpl_data = out_stream.read()

        if self.env.context.get("report_py3o_skip_conversion"):
            return result_path

        result_path = self._convert_single_report(result_path, model_instance, data)

        return self._postprocess_report(model_instance, result_path)

    def _convert_single_report(self, result_path, model_instance, data):
        """Run a command to convert to our target format"""
        if not self.ir_actions_report_id.is_py3o_native_format:
            with tempfile.TemporaryDirectory() as tmp_user_installation:
                command = self._convert_single_report_cmd(
                    result_path,
                    model_instance,
                    data,
                    user_installation=tmp_user_installation,
                )
                logger.debug("Running command %s", command)
                output = subprocess.check_output(
                    command, cwd=os.path.dirname(result_path)
                )
                logger.debug("Output was %s", output)
                self._cleanup_tempfiles([result_path])
                result_path, result_filename = os.path.split(result_path)
                result_path = os.path.join(
                    result_path,
                    "%s.%s"
                    % (
                        os.path.splitext(result_filename)[0],
                        self.ir_actions_report_id.py3o_filetype,
                    ),
                )
        return result_path

    def _convert_single_report_cmd(
        self, result_path, model_instance, data, user_installation=None
    ):
        """Return a command list suitable for use in subprocess.call"""
        lo_bin = self.ir_actions_report_id.lo_bin_path
        if not lo_bin:
            raise RuntimeError(
                _(
                    "Libreoffice runtime not available. "
                    "Please contact your administrator."
                )
            )
        cmd = [
            lo_bin,
            "--headless",
            "--convert-to",
            self.ir_actions_report_id.py3o_filetype,
            result_path,
        ]
        if user_installation:
            cmd.append("-env:UserInstallation=file:%s" % user_installation)
        return cmd

    def _get_or_create_single_report(
        self, model_instance, data, existing_reports_attachment
    ):
        self.ensure_one()
        attachment = existing_reports_attachment.get(model_instance.id)
        if attachment and self.ir_actions_report_id.attachment_use:
            content = base64.b64decode(attachment.datas)
            report_file = tempfile.mktemp("." + self.ir_actions_report_id.py3o_filetype)
            with open(report_file, "wb") as f:
                f.write(content)
            return report_file
        return self._create_single_report(model_instance, data)

    def _zip_results(self, reports_path):
        self.ensure_one()
        zfname_prefix = self.ir_actions_report_id.name
        result_path = tempfile.mktemp(suffix="zip", prefix="py3o-zip-result")
        with ZipFile(result_path, "w", ZIP_DEFLATED) as zf:
            cpt = 0
            for report in reports_path:
                fname = "%s_%d.%s" % (zfname_prefix, cpt, report.split(".")[-1])
                zf.write(report, fname)

                cpt += 1
        return result_path

    @api.model
    def _merge_pdf(self, reports_path):
        """Merge PDF files into one.

        :param reports_path: list of path of pdf files
        :returns: path of the merged pdf
        """
        writer = PdfFileWriter()
        for path in reports_path:
            reader = PdfFileReader(path)
            writer.appendPagesFromReader(reader)
        merged_file_fd, merged_file_path = tempfile.mkstemp(
            suffix=".pdf", prefix="report.merged.tmp."
        )
        with closing(os.fdopen(merged_file_fd, "wb")) as merged_file:
            writer.write(merged_file)
        return merged_file_path

    def _merge_results(self, reports_path):
        self.ensure_one()
        filetype = self.ir_actions_report_id.py3o_filetype
        if not reports_path:
            return False, False
        if len(reports_path) == 1:
            return reports_path[0], filetype
        if filetype == formats.FORMAT_PDF:
            return self._merge_pdf(reports_path), formats.FORMAT_PDF
        else:
            return self._zip_results(reports_path), "zip"

    @api.model
    def _cleanup_tempfiles(self, temporary_files):
        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except OSError:
                logger.error("Error when trying to remove file %s" % temporary_file)

    def create_report(self, res_ids, data):
        """Override this function to handle our py3o report"""
        model_instances = self.env[self.ir_actions_report_id.model].browse(res_ids)
        reports_path = []
        if len(res_ids) > 1 and self.ir_actions_report_id.py3o_multi_in_one:
            reports_path.append(self._create_single_report(model_instances, data))
        else:
            existing_reports_attachment = self.ir_actions_report_id._get_attachments(
                res_ids
            )
            for model_instance in model_instances:
                reports_path.append(
                    self._get_or_create_single_report(
                        model_instance, data, existing_reports_attachment
                    )
                )

        result_path, filetype = self._merge_results(reports_path)
        reports_path.append(result_path)

        # Here is a little joke about Odoo
        # we do all the generation process using files to avoid memory
        # consumption...
        # ... but odoo wants the whole data in memory anyways :)

        with open(result_path, "r+b") as fd:
            res = fd.read()
        self._cleanup_tempfiles(set(reports_path))
        return res, filetype
