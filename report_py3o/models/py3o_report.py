# Copyright 2013 XCG Consulting (http://odoo.consulting)
# Copyright 2016 ACSONE SA/NV
# Copyright 2018 - Brain-tec AG - Carlos Jesus Cebrian
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import base64
from base64 import b64decode
from io import BytesIO

import logging
import os
import cgi
from contextlib import closing
import subprocess
import time

import pkg_resources
import sys
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from odoo.exceptions import AccessError
from . import report_sxw
from odoo import api, fields, models, tools, _
from odoo.tools.safe_eval import safe_eval

logger = logging.getLogger(__name__)

try:
    from py3o.template import Template
    from py3o import formats
    from genshi.core import Markup
except ImportError:
    logger.debug('Cannot import py3o.template')
try:
    from py3o.formats import Formats, UnkownFormatException
except ImportError:
    logger.debug('Cannot import py3o.formats')


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


def format_multiline_value(value):
    if value:
        return Markup(cgi.escape(value).replace('\n', '<text:line-break/>').
                      replace('\t', '<text:s/><text:s/><text:s/><text:s/>'))
    return ""


@py3o_report_extender()
def default_extend(report_xml, localcontext):
    # add the base64decode function to be able do decode binary fields into
    # the template
    localcontext['b64decode'] = b64decode
    localcontext['report_xml'] = report_xml
    localcontext['format_multiline_value'] = format_multiline_value
    localcontext['html_sanitize'] = tools.html2plaintext


class Py3oReport(models.TransientModel):
    _name = "py3o.report"
    _description = "Report Py30"

    ir_actions_report_id = fields.Many2one(
        comodel_name="ir.actions.report",
        required=True
    )

    @api.multi
    def _is_valid_template_path(self, path):
        """ Check if the path is a trusted path for py3o templates.
        """
        real_path = os.path.realpath(path)
        root_path = tools.config.get_misc('report_py3o', 'root_tmpl_path')
        if not root_path:
            logger.warning(
                "You must provide a root template path into odoo.cfg to be "
                "able to use py3o template configured with an absolute path "
                "%s", real_path)
            return False
        is_valid = real_path.startswith(root_path + os.path.sep)
        if not is_valid:
            logger.warning(
                "Py3o template path is not valid. %s is not a child of root "
                "path %s", real_path, root_path)
        return is_valid

    @api.multi
    def _is_valid_template_filename(self, filename):
        """ Check if the filename can be used as py3o template
        """
        if filename and os.path.isfile(filename):
            fname, ext = os.path.splitext(filename)
            ext = ext.replace('.', '')
            try:
                fformat = Formats().get_format(ext)
                if fformat and fformat.native:
                    return True
            except UnkownFormatException:
                logger.warning("Invalid py3o template %s", filename,
                               exc_info=1)
        logger.warning(
            '%s is not a valid Py3o template filename', filename)
        return False

    @api.multi
    def _get_template_from_path(self, tmpl_name):
        """ Return the template from the path to root of the module if specied
        or an absolute path on your server
        """
        if not tmpl_name:
            return None
        report_xml = self.ir_actions_report_id
        flbk_filename = None
        if report_xml.module:
            # if the default is defined
            flbk_filename = pkg_resources.resource_filename(
                "odoo.addons.%s" % report_xml.module,
                tmpl_name,
            )
        elif self._is_valid_template_path(tmpl_name):
            flbk_filename = os.path.realpath(tmpl_name)
        if self._is_valid_template_filename(flbk_filename):
            with open(flbk_filename, 'r') as tmpl:
                return tmpl.read()
        return None

    @api.multi
    def _get_template_fallback(self, model_instance):
        """
        Return the template referenced in the report definition
        :return:
        """
        self.ensure_one()
        report_xml = self.ir_actions_report_id
        return self._get_template_from_path(report_xml.py3o_template_fallback)

    @api.multi
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
        if report_xml.py3o_template_id and report_xml.py3o_template_id.id:
            # if a user gave a report template
            tmpl_data = b64decode(
                report_xml.py3o_template_id.py3o_template_data
            )

        else:
            tmpl_data = self._get_template_fallback(model_instance)

        if tmpl_data is None:
            # if for any reason the template is not found
            raise TemplateNotFound(
                _('No template found. Aborting.'),
                sys.exc_info(),
            )

        return tmpl_data

    @api.multi
    def _extend_parser_context(self, context_instance, report_xml):
        # add default extenders
        for fct in _extender_functions.get(None, []):
            fct(report_xml, context_instance.localcontext)
        # add extenders for registered on the template
        xml_id = report_xml.get_external_id().get(report_xml.id)
        if xml_id in _extender_functions:
            for fct in _extender_functions[xml_id]:
                fct(report_xml, context_instance.localcontext)

    @api.multi
    def _get_parser_context(self, model_instance, data):
        report_xml = self.ir_actions_report_id
        context_instance = report_sxw.rml_parse(self.env.cr, self.env.uid,
                                                report_xml.name,
                                                context=self.env.context)
        context_instance.set_context(model_instance, data, model_instance.ids,
                                     report_xml.report_type)
        self._extend_parser_context(context_instance, report_xml)
        return context_instance.localcontext

    @api.model
    def _postprocess_report(self, report_path, res_id, save_in_attachment):
        if save_in_attachment.get(res_id):
            with open(report_path, 'rb') as report:
                attachment = {
                    'name': save_in_attachment.get(res_id),
                    'datas': base64.encodebytes(report.read()),
                    'datas_fname': save_in_attachment.get(res_id),
                    'res_model': save_in_attachment.get('model'),
                    'res_id': res_id,
                }
                try:
                    self.env['ir.attachment'].create(attachment)
                except AccessError:
                    logger.info("Cannot save report %r as attachment",
                                attachment['name'])
                else:
                    logger.info(
                        'The document %s is now saved in the database',
                        attachment['name'])

    @api.multi
    def _create_single_report(self, model_instance, data, save_in_attachment):
        """ This function to generate our py3o report
        """
        self.ensure_one()
        result_fd, result_path = tempfile.mkstemp(
            suffix='.ods', prefix='p3o.report.tmp.')
        tmpl_data = self.get_template(model_instance)

        in_stream = BytesIO(tmpl_data)
        with closing(os.fdopen(result_fd, 'wb+')) as out_stream:
            template = Template(in_stream, out_stream, escape_false=True)
            localcontext = self._get_parser_context(model_instance, data)
            template.render(localcontext)
            out_stream.seek(0)
            tmpl_data = out_stream.read()

        if self.env.context.get('report_py3o_skip_conversion'):
            return result_path

        result_path = self._convert_single_report(
            result_path, model_instance, data
        )

        if len(model_instance) == 1:
            self._postprocess_report(
                result_path, model_instance.id, save_in_attachment)

        return result_path

    @api.multi
    def _convert_single_report(self, result_path, model_instance, data):
        """Run a command to convert to our target format"""
        filetype = self.ir_actions_report_id.py3o_filetype
        if not Formats().get_format(filetype).native:
            command = self._convert_single_report_cmd(
                result_path, model_instance, data,
            )
            logger.debug('Running command %s', command)
            output = subprocess.check_output(
                command, cwd=os.path.dirname(result_path),
            )
            logger.debug('Output was %s', output)
            self._cleanup_tempfiles([result_path])
            result_path, result_filename = os.path.split(result_path)
            result_path = os.path.join(
                result_path, '%s.%s' % (
                    os.path.splitext(result_filename)[0], filetype
                )
            )
        return result_path

    @api.multi
    def _convert_single_report_cmd(self, result_path, model_instance, data):
        """Return a command list suitable for use in subprocess.call"""
        return [
            self.env['ir.config_parameter'].get_param(
                'py3o.conversion_command', 'libreoffice',
            ),
            '--headless',
            '--convert-to',
            self.ir_actions_report_id.py3o_filetype,
            result_path,
        ]

    @api.multi
    def _get_or_create_single_report(self, model_instance, data,
                                     save_in_attachment):
        self.ensure_one()
        if save_in_attachment and save_in_attachment[
                'loaded_documents'].get(model_instance.id):
            d = save_in_attachment[
                'loaded_documents'].get(model_instance.id)
            report_file = tempfile.mktemp(
                "." + self.ir_actions_report_id.py3o_filetype)
            with open(report_file, "wb") as f:
                f.write(d)
            return report_file
        return self._create_single_report(
            model_instance, data, save_in_attachment)

    @api.multi
    def _zip_results(self, reports_path):
        self.ensure_one()
        zfname_prefix = self.ir_actions_report_id.name
        result_path = tempfile.mktemp(suffix="zip", prefix='py3o-zip-result')
        with ZipFile(result_path, 'w', ZIP_DEFLATED) as zf:
            cpt = 0
            for report in reports_path:
                fname = "%s_%d.%s" % (
                    zfname_prefix, cpt, report.split('.')[-1])
                zf.write(report, fname)

                cpt += 1
        return result_path

    @api.multi
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
            return self._zip_results(reports_path), 'zip'

    @api.model
    def _cleanup_tempfiles(self, temporary_files):
        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                logger.error(
                    'Error when trying to remove file %s' % temporary_file)

    @api.multi
    def create_report(self, res_ids, data):
        """ Override this function to handle our py3o report
        """
        model_instances = self.env[self.ir_actions_report_id.model].browse(
            res_ids)
        save_in_attachment = self._check_attachment_use(
            res_ids, self.ir_actions_report_id) or {}
        reports_path = []
        if (
                len(res_ids) > 1 and
                self.ir_actions_report_id.py3o_multi_in_one):
            reports_path.append(
                self._create_single_report(
                    model_instances, data, save_in_attachment))
        else:
            for model_instance in model_instances:
                reports_path.append(
                    self._get_or_create_single_report(
                        model_instance, data, save_in_attachment))

        result_path, filetype = self._merge_results(reports_path)
        reports_path.append(result_path)

        # Here is a little joke about Odoo
        # we do all the generation process using files to avoid memory
        # consumption...
        # ... but odoo wants the whole data in memory anyways :)

        with open(result_path, 'r+b') as fd:
            res = fd.read()
        self._cleanup_tempfiles(set(reports_path))
        return res, filetype

    @api.model
    def _check_attachment_use(self, docids, report):
        """ Check attachment_use field. If set to true and an existing pdf is
         already saved, load this one now. Else, mark save it.
        """
        save_in_attachment = {}
        save_in_attachment['model'] = report.model
        save_in_attachment['loaded_documents'] = {}

        if report.attachment:
            records = self.env[report.model].browse(docids)
            filenames = self._attachment_filename(records, report)
            attachments = None
            if report.attachment_use:
                attachments = self._attachment_stored(
                    records, report, filenames=filenames)
            for record_id in docids:
                filename = filenames[record_id]
                if attachments:
                    attachment = attachments[record_id]
                    if attachment:
                        file_attached = attachment.datas
                        file_attached = base64.decodebytes(file_attached)
                        save_in_attachment['loaded_documents'][record_id] = file_attached

                        continue

                if filename is False:
                    continue
                else:
                    save_in_attachment[record_id] = filename

        return save_in_attachment

    @api.model
    def _attachment_filename(self, records, report):
        return dict(
            (record.id, safe_eval(
                report.attachment, {
                    'object': record, 'time': time})) for record in records)

    @api.model
    def _attachment_stored(self, records, report, filenames=None):
        if not filenames:
            filenames = self._attachment_filename(records, report)
            return dict((record.id, self.env['ir.attachment'].search([
                ('data_fname', '=', filenames[record.id]),
                ('res_model', '=', report.model),
                ('res_id', '=', record.id)
            ], limit=1)) for record in records)
