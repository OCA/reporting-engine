# -*- coding: utf-8 -*-
# Copyright 2013 XCG Consulting (http://odoo.consulting)
# Copyright 2016 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)
import base64
from base64 import b64decode
from cStringIO import StringIO
import json
import logging
import os
from contextlib import closing

import pkg_resources
import requests
import sys
import tempfile
from zipfile import ZipFile, ZIP_DEFLATED

from odoo.exceptions import AccessError
from odoo.exceptions import UserError
from odoo.report.report_sxw import rml_parse
from odoo import api, fields, models, _

logger = logging.getLogger(__name__)

try:
    from py3o.template.helpers import Py3oConvertor
    from py3o.template import Template
    from py3o import formats
except ImportError:
    logger.debug('Cannot import py3o.template')
try:
    from py3o.formats import Formats
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


@py3o_report_extender()
def defautl_extend(report_xml, localcontext):
    # add the base64decode function to be able do decode binary fields into
    # the template
    localcontext['b64decode'] = b64decode
    localcontext['report_xml'] = report_xml


class Py3oReport(models.TransientModel):
    _name = "py3o.report"
    _inherit = 'report'
    _description = "Report Py30"

    ir_actions_report_xml_id = fields.Many2one(
        comodel_name="ir.actions.report.xml",
        required=True
    )

    @api.multi
    def _get_template_from_path(self, tmpl_name):
        """"Return the template from the path to root of the module if specied
        or an absolute path on your server
        """
        if not tmpl_name:
            return None
        report_xml = self.ir_actions_report_xml_id
        flbk_filename = None
        if report_xml.module:
            # if the default is defined
            flbk_filename = pkg_resources.resource_filename(
                "odoo.addons.%s" % report_xml.module,
                tmpl_name,
            )
        elif os.path.isabs(tmpl_name):
            # It is an absolute path
            flbk_filename = os.path.normcase(os.path.normpath(tmpl_name))
        if flbk_filename and os.path.exists(flbk_filename):
            # and it exists on the fileystem
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
        report_xml = self.ir_actions_report_xml_id
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
        report_xml = self.ir_actions_report_xml_id
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
                _(u'No template found. Aborting.'),
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
        report_xml = self.ir_actions_report_xml_id
        context_instance = rml_parse(self.env.cr, self.env.uid,
                                     report_xml.name,
                                     context=self.env.context)
        context_instance.set_context(model_instance, data, model_instance.ids,
                                     report_xml.report_type)
        self._extend_parser_context(context_instance, report_xml)
        return context_instance.localcontext

    @api.model
    def _postprocess_report(self, report_path, res_id, save_in_attachment):
        if save_in_attachment.get(res_id):
            with open(report_path, 'rb') as pdfreport:
                attachment = {
                    'name': save_in_attachment.get(res_id),
                    'datas': base64.encodestring(pdfreport.read()),
                    'datas_fname': save_in_attachment.get(res_id),
                    'res_model': save_in_attachment.get('model'),
                    'res_id': res_id,
                }
                try:
                    self.env['ir.attachment'].create(attachment)
                except AccessError:
                    logger.info("Cannot save PDF report %r as attachment",
                                attachment['name'])
                else:
                    logger.info(
                        'The PDF document %s is now saved in the database',
                        attachment['name'])

    @api.multi
    def _create_single_report(self, model_instance, data, save_in_attachment):
        """ This function to generate our py3o report
        """
        self.ensure_one()
        report_xml = self.ir_actions_report_xml_id
        filetype = report_xml.py3o_filetype
        result_fd, result_path = tempfile.mkstemp(
            suffix='.' + filetype, prefix='p3o.report.tmp.')
        tmpl_data = self.get_template(model_instance)

        in_stream = StringIO(tmpl_data)
        with closing(os.fdopen(result_fd, 'w+')) as out_stream:
            template = Template(in_stream, out_stream, escape_false=True)
            localcontext = self._get_parser_context(model_instance, data)
            is_native = Formats().get_format(filetype).native
            if report_xml.py3o_is_local_fusion:
                template.render(localcontext)
                out_stream.seek(0)
                in_stream = out_stream.read()
                datadict = {}
            else:
                expressions = template.get_all_user_python_expression()
                py_expression = template.convert_py3o_to_python_ast(
                    expressions)
                convertor = Py3oConvertor()
                data_struct = convertor(py_expression)
                datadict = data_struct.render(localcontext)

        if not is_native or not report_xml.py3o_is_local_fusion:
            # Call py3o.server to render the template in the desired format
            files = {
                'tmpl_file': in_stream,
            }
            fields = {
                "targetformat": filetype,
                "datadict": json.dumps(datadict),
                "image_mapping": "{}",
            }
            if report_xml.py3o_is_local_fusion:
                fields['skipfusion'] = '1'
            r = requests.post(
                report_xml.py3o_server_id.url, data=fields, files=files)
            if r.status_code != 200:
                # server says we have an issue... let's tell that to enduser
                raise UserError(
                    _('Fusion server error %s') % r.text,
                )

            chunk_size = 1024
            with open(result_path, 'w+') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)
        self._postprocess_report(
            result_path, model_instance.id, save_in_attachment)
        return result_path

    @api.multi
    def _get_or_create_single_report(self, model_instance, data,
                                     save_in_attachment):
        self.ensure_one()
        if save_in_attachment and save_in_attachment[
                'loaded_documents'].get(model_instance.id):
            d = save_in_attachment[
                'loaded_documents'].get(model_instance.id)
            return d, self.ir_actions_report_xml_id.py3o_filetype
        return self._create_single_report(
            model_instance, data, save_in_attachment)

    @api.multi
    def _zip_results(self, reports_path):
        self.ensure_one()
        zfname_prefix = self.ir_actions_report_xml_id.name
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
        filetype = self.ir_actions_report_xml_id.py3o_filetype
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
        model_instances = self.env[self.ir_actions_report_xml_id.model].browse(
            res_ids)
        save_in_attachment = self._check_attachment_use(
            res_ids, self.ir_actions_report_xml_id) or {}
        reports_path = []
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
