# Copyright 2013 XCG Consulting (http://odoo.consulting)
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import logging
import os
import subprocess
import sys
import tempfile
import warnings
from configparser import ConfigParser
from contextlib import closing
from datetime import datetime, timezone
from importlib.resources import files
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from odoo import api, fields, models
from odoo.exceptions import AccessError
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval, time

from ..models._py3o_parser_context import Py3oParserContext

logger = logging.getLogger(__name__)

try:
    # Preferred source when available: structured [report_py3o] section provided
    # by OCA's server_environment addon.
    from odoo.addons.server_environment import serv_config

    if serv_config.has_section("report_py3o"):
        report_py3o_config = serv_config["report_py3o"]
    else:
        report_py3o_config = {}
except ImportError:
    # No server_environment: try to read a [report_py3o] section from odoo.conf
    report_py3o_config = {}
    cfg_path = config.get("config")
    if cfg_path:
        cp = ConfigParser(interpolation=None)
        cp.read(cfg_path)
        if cp.has_section("report_py3o"):
            report_py3o_config = dict(cp["report_py3o"])

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
    from pypdf import PdfReader, PdfWriter
except ImportError:
    logger.debug("Cannot import pypdf")
try:
    import uno
except ImportError:
    logger.debug("Cannot import uno")
    uno = False
try:
    from com.sun.star.beans import PropertyValue
except ImportError:
    logger.debug("Cannot import com.sun.star.beans")

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
        root_path = report_py3o_config.get("root_tmpl_path") or config.get(
            "root_tmpl_path"
        )
        if root_path:
            root_path = os.path.realpath(root_path.strip()).rstrip(os.path.sep)
        if not root_path:
            logger.warning(
                "You must provide a root template path into odoo.cfg to be "
                "able to use py3o template configured with an absolute path "
                "%s",
                real_path,
            )
            return False
        try:
            is_valid = os.path.commonpath([root_path, real_path]) == root_path
        except ValueError:
            is_valid = False
        if not is_valid:
            logger.warning(
                "Py3o template path is not valid. %s is not a child of root path %s",
                real_path,
                root_path,
            )
        return is_valid

    def _is_valid_template_filename(self, filename):
        """Check if the filename can be used as py3o template"""
        if filename and os.path.isfile(filename):
            _fname, ext = os.path.splitext(filename)
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
            flbk_filename = files(f"odoo.addons.{report_xml.module}").joinpath(
                tmpl_name
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
            tmpl_data = report_xml.py3o_template_id.py3o_template_data.content

        else:
            tmpl_data = self._get_template_fallback(model_instance)

        if tmpl_data is None:
            # if for any reason the template is not found
            raise TemplateNotFound(
                self.env._("No template found. Aborting."), sys.exc_info()
            )

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
        context.update(
            report_xml._get_rendering_context(report_xml, model_instance.ids, data)
        )
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
                attachment_name = safe_eval(
                    self.ir_actions_report_id.attachment,
                    {"object": model_instance, "time": time},
                )
                if attachment_name:
                    attachment_vals = {
                        "name": attachment_name,
                        "res_model": self.ir_actions_report_id.model,
                        "res_id": model_instance.id,
                        "raw": buffer.getvalue(),
                    }
                    try:
                        attach = self.env["ir.attachment"].create(attachment_vals)
                    except AccessError:
                        logger.info(
                            "Cannot save PDF report %s as attachment",
                            attachment_vals["name"],
                        )
                    else:
                        logger.info(
                            "PDF document %s saved as attachment ID %d",
                            attachment_vals["name"],
                            attach.id,
                        )
        return result_path

    def _create_single_report(self, model_instance, data):
        """This function to generate our py3o report"""
        self.ensure_one()
        result_fd, result_path = tempfile.mkstemp(
            suffix=".odt", prefix="py3o.report.tmp."
        )
        tmpl_data = self.get_template(model_instance)

        in_stream = BytesIO(tmpl_data)
        with closing(os.fdopen(result_fd, "wb+")) as out_stream:
            template = Template(in_stream, out_stream, escape_false=True)
            localcontext = self._get_parser_context(model_instance, data)
            template.render(localcontext)
            out_stream.seek(0)
            tmpl_data = out_stream.read()
        logger.debug("Input result_path=%s", result_path)

        report = self.ir_actions_report_id
        py3o_server = report.py3o_server_id
        if py3o_server and not uno:
            logger.warning("UNO is not loaded: falling back to spawning LibreOffice")
        if not py3o_server or not uno:
            result_path = self._convert_single_report(result_path, model_instance, data)
            return self._postprocess_report(model_instance, result_path)
        filetype = report.py3o_filetype
        uno_filter_data = []
        if filetype == "pdf":
            options = report.pdf_options_id or py3o_server.pdf_options_id
            if options:
                pdf_options_dict = options.odoo2libreoffice_options()
                logger.debug("PDF export options: %s", pdf_options_dict)
                for pdf_opt_key, pdf_opt_val in pdf_options_dict.items():
                    if isinstance(pdf_opt_val, bool | int | str) and isinstance(
                        pdf_opt_key, str
                    ):
                        uno_filter_data.append(
                            PropertyValue(Name=pdf_opt_key, Value=pdf_opt_val)
                        )

        logger.info(
            "Connecting to LibreOffice on %s to convert report %s to %s",
            py3o_server.display_name,
            report.report_name,
            filetype,
        )
        start_chrono = datetime.now(tz=timezone.utc)
        uno_local_ctx = uno.getComponentContext()
        uno_resolver = uno_local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", uno_local_ctx
        )
        uno_url = (
            f"uno:socket,host={py3o_server.host.strip()},"
            f"port={py3o_server.port};urp;StarOffice.ComponentContext"
        )
        logger.debug("uno_url=%s", uno_url)
        try:
            uno_ctx = uno_resolver.resolve(uno_url)
            logger.info(
                "Connection to LibreOffice established on %s", py3o_server.display_name
            )
        except Exception as e:
            logger.warning(
                "Failed to connect to LibreOffice on %s. Error: %s",
                py3o_server.display_name,
                e,
            )
            result_path = self._convert_single_report(result_path, model_instance, data)
            return self._postprocess_report(model_instance, result_path)

        uno_desktop = uno_ctx.getByName("/singletons/com.sun.star.frame.theDesktop")

        uno_import_url = uno.systemPathToFileUrl(result_path)
        uno_input_properties = [PropertyValue(Name="ReadOnly", Value=True)]

        try:
            # API doc: https://api.libreoffice.org/docs/idl/ref/
            # interfacecom_1_1sun_1_1star_1_1frame_1_1XComponentLoader.html
            uno_document = uno_desktop.loadComponentFromURL(
                uno_import_url, "_default", 0, uno_input_properties
            )
            logger.info("LibreOffice successfully loaded the document")
        except Exception as e:
            logger.warning(
                "LibreOffice failed to load the document from %s. Error: %s",
                uno_import_url,
                e,
            )
            result_path = self._convert_single_report(result_path, model_instance, data)
            return self._postprocess_report(model_instance, result_path)
        if not uno_document:
            logger.warning(
                "LibreOffice failed to load the document from %s. No specific error.",
                uno_import_url,
            )
            result_path = self._convert_single_report(result_path, model_instance, data)
            return self._postprocess_report(model_instance, result_path)
        # It doesn't work when the same path is used as input and output,
        # so we create a file dedicated to the output
        _out_fd, out_result_path = tempfile.mkstemp(
            prefix="py3o.report.tmp.", suffix=f".{filetype}"
        )
        logger.debug("out_result_path=%s", out_result_path)
        uno_out_url = uno.systemPathToFileUrl(out_result_path)
        # py3o.formats doesn't take into account the source format to decide
        # the right filter. For pdf, il will always give "writer_pdf_Export"
        # although we should use "calc_pdf_Export" if source document is ODS
        # TODO stop using py3o.formats and re-write this mess
        uno_filtername = Formats()._formats[filetype].odfname
        logger.debug("uno_filtername=%s uno_out_url=%s", uno_filtername, uno_out_url)
        uno_output_properties = [
            PropertyValue(Name="FilterName", Value=uno_filtername),
            PropertyValue(Name="Overwrite", Value=True),
            PropertyValue(
                Name="FilterData",
                Value=uno.Any("[]com.sun.star.beans.PropertyValue", uno_filter_data),
            ),
        ]
        try:
            uno_document.storeToURL(uno_out_url, uno_output_properties)
        except Exception as err:
            logger.warning(
                "Conversion of report %s to %s with LibreOffice failed. Error: %s",
                report.report_name,
                filetype,
                err,
            )
            logger.warning(
                "Make sure the source format can really be converted to %s.", filetype
            )
            result_path = self._convert_single_report(result_path, model_instance, data)
            return self._postprocess_report(model_instance, result_path)
        finally:
            # Should we call uno_desktop.terminate() ??
            uno_document.close(True)
            logger.debug("document has been closed.")

        # TODO: test that the output has the right format
        # by analysing the beginning of the file
        # To trigger the bug: change "FilterName" by "toto" in uno_output_properties
        end_chrono = datetime.now(tz=timezone.utc)
        convert_seconds = (end_chrono - start_chrono).total_seconds()
        logger.info(
            "Report %s converted to %s in %s seconds",
            report.report_name,
            filetype,
            convert_seconds,
        )
        if len(model_instance) == 1:
            self._postprocess_report(model_instance, out_result_path)
        return out_result_path

    def _convert_single_report(self, result_path, model_instance, data):
        """Run a command to convert to our target format"""
        report = self.ir_actions_report_id
        filetype = report.py3o_filetype
        if not report.is_py3o_native_format:
            logger.info(
                f"Spawning LibreOffice to convert report {report.report_name} "
                f"to {filetype}"
            )
            start_chrono = datetime.now(tz=timezone.utc)
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
                    f"{os.path.splitext(result_filename)[0]}.{filetype}",
                )
            end_chrono = datetime.now(tz=timezone.utc)
            convert_seconds = (end_chrono - start_chrono).total_seconds()
            logger.info(
                f"Report {report.report_name} converted to {filetype} in "
                f"{convert_seconds} seconds"
            )
        return result_path

    def _convert_single_report_cmd(
        self, result_path, model_instance, data, user_installation=None
    ):
        """Return a command list suitable for use in subprocess.call"""
        lo_bin = self.ir_actions_report_id.lo_bin_path
        if not lo_bin:
            raise RuntimeError(
                self.env._(
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
            cmd.append(f"-env:UserInstallation=file:{user_installation}")
        return cmd

    def _get_or_create_single_report(
        self, model_instance, data, existing_reports_attachment
    ):
        self.ensure_one()
        attachment = existing_reports_attachment.get(model_instance.id)
        if attachment and self.ir_actions_report_id.attachment_use:
            content = attachment.raw.content
            fd, report_file = tempfile.mkstemp(
                "." + self.ir_actions_report_id.py3o_filetype
            )
            os.close(fd)
            with open(report_file, "wb") as f:
                f.write(content)
            return report_file
        return self._create_single_report(model_instance, data)

    def _zip_results(self, reports_path):
        self.ensure_one()
        fd, result_path = tempfile.mkstemp(suffix=".zip", prefix="py3o-zip-result")
        os.close(fd)
        with ZipFile(result_path, "w", ZIP_DEFLATED) as zf:
            for report_instance, report in reports_path.items():
                fname = self.ir_actions_report_id.gen_report_download_filename(
                    report_instance.ids, {}
                )
                zf.write(report, fname)
        return result_path

    @api.model
    def _merge_pdf(self, reports_path):
        """Merge PDF files into one.

        :param reports_path: list of path of pdf files
        :returns: path of the merged pdf
        """
        writer = PdfWriter()
        for path in reports_path:
            reader = PdfReader(path)
            writer.append_pages_from_reader(reader)
        merged_file_fd, merged_file_path = tempfile.mkstemp(
            suffix=".pdf", prefix="report.merged.tmp."
        )
        with closing(os.fdopen(merged_file_fd, "wb")) as merged_file:
            writer.write(merged_file)
        return merged_file_path

    def _merge_results(self, reports_path):
        self.ensure_one()
        filetype = self.ir_actions_report_id.py3o_filetype
        path_list = list(reports_path.values())
        if not reports_path:
            return False, False
        if len(reports_path) == 1:
            return path_list[0], filetype
        if filetype == formats.FORMAT_PDF:
            return self._merge_pdf(path_list), formats.FORMAT_PDF
        else:
            return self._zip_results(reports_path), "zip"

    @api.model
    def _cleanup_tempfiles(self, temporary_files):
        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except OSError:
                logger.error(f"Error when trying to remove file {temporary_file}")

    def create_report(self, res_ids, data):
        """Override this function to handle our py3o report"""
        model_instances = self.env[self.ir_actions_report_id.model].browse(res_ids)
        reports_path = {}
        if len(res_ids) > 1 and self.ir_actions_report_id.py3o_multi_in_one:
            reports_path[model_instances] = self._create_single_report(
                model_instances, data
            )
        else:
            existing_reports_attachment = self.ir_actions_report_id._get_attachments(
                res_ids
            )
            for model_instance in model_instances:
                reports_path[model_instance] = self._get_or_create_single_report(
                    model_instance, data, existing_reports_attachment
                )

        result_path, filetype = self._merge_results(reports_path)
        cleanup_path = list(reports_path.values())
        cleanup_path.append(result_path)

        # Here is a little joke about Odoo
        # we do all the generation process using files to avoid memory
        # consumption...
        # ... but odoo wants the whole data in memory anyways :)

        with open(result_path, "r+b") as fd:
            res = fd.read()
        self._cleanup_tempfiles(set(cleanup_path))
        return res, filetype
