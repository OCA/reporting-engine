# -*- encoding: utf-8 -*-
import pkg_resources
import os
import sys
from base64 import b64decode
import requests
from tempfile import NamedTemporaryFile
from openerp import _
from openerp.report.report_sxw import report_sxw, rml_parse
from openerp import registry
from openerp.exceptions import DeferredException

from py3o.template import Template


_extender_functions = {}


class TemplateNotFound(DeferredException):
    pass


def py3o_report_extender(report_name):
    """
    A decorator to define function to extend the context sent to a template.
    This will be called at the creation of the report.
    The following arguments will be passed to it:
        - pool: the model pool
        - cr: the database cursor
        - uid: the id of the user that call the renderer
        - localcontext: The context that will be passed to the report engine
        - context: the Odoo context

    Method copied from CampToCamp report_webkit module.

    :param report_name: xml id of the report
    :return: a decorated class
    """
    def fct1(fct):
        lst = _extender_functions.get(report_name)
        if not lst:
            lst = []
            _extender_functions[report_name] = lst
        lst.append(fct)
        return fct
    return fct1


class Py3oParser(report_sxw):
    """Custom class that use Py3o to render libroffice reports.
        Code partially taken from CampToCamp's webkit_report."""

    def __init__(self, name, table, rml=False, parser=rml_parse,
                 header=False, store=False, register=True):
        self.localcontext = {}
        super(Py3oParser, self).__init__(
            name, table, rml=rml, parser=parser,
            header=header, store=store, register=register
        )

    def get_template(self, report_obj):
        """private helper to fetch the template data either from the database
        or from the default template file provided by the implementer.

        ATM this method takes a report definition recordset
        to try and fetch the report template from database. If not found it will
        fallback to the template file referenced in the report definition.

        @param report_obj: a recordset representing the report defintion
        @type report_obj: openerp.model.recordset instance

        @returns: string or buffer containing the template data

        @raises: TemplateNotFound which is a subclass of
        openerp.exceptions.DeferredException
        """

        tmpl_data = None

        if report_obj.py3o_template_id and report_obj.py3o_template_id.id:
            # if a user gave a report template
            tmpl_data = b64decode(
                report_obj.py3o_template_id.py3o_template_data
            )

        elif report_obj.py3o_template_fallback and report_obj.module:
            # if the default is defined
            flbk_filename = pkg_resources.resource_filename(
                "openerp.addons.%s" % report_obj.module,
                report_obj.py3o_template_fallback,
            )
            if os.path.exists(flbk_filename):
                # and it exists on the fileystem
                with open(flbk_filename, 'r') as tmpl:
                    tmpl_data = tmpl.read()

        if tmpl_data is None:
            # if for any reason the template is not found
            print("*"*35)
            print("Template filename: %s" % flbk_filename)
            print("*"*35)

            raise TemplateNotFound(
                _(u'No template found. Aborting.'),
                sys.exc_info(),
            )

        return tmpl_data

    def create_single_pdf(self, cr, uid, ids, data, report_xml, context=None):
        """ Overide this function to generate our py3o report
        """
        if report_xml.report_type != 'py3o':
            return super(Py3oParser, self).create_single_pdf(
                cr, uid, ids, data, report_xml, context=context
            )

        pool = registry(cr.dbname)
        model_data_ids = pool['ir.model.data'].search(
            cr, uid, [
                ('model', '=', 'ir.actions.report.xml'),
                ('res_id', '=', report_xml.id),
            ]
        )

        xml_id = None
        if model_data_ids:
            model_data = pool['ir.model.data'].browse(
                cr, uid, model_data_ids[0], context=context
            )
            xml_id = '%s.%s' % (model_data.module, model_data.name)

        parser_instance = self.parser(cr, uid, self.name2, context=context)
        parser_instance.set_context(
            self.getObjects(cr, uid, ids, context),
            data, ids, report_xml.report_type
        )

        if xml_id in _extender_functions:
            for fct in _extender_functions[xml_id]:
                fct(pool, cr, uid, parser_instance.localcontext, context)

        template = report_xml.py3o_template_id
        filetype = report_xml.py3o_fusion_filetype

        tmpl_data = self.get_template(report_xml)

# py3o.template operates on filenames so create temporary files.
        with NamedTemporaryFile(
            suffix='.odt',
            prefix='py3o-template-') as in_temp, NamedTemporaryFile(
                suffix='.odt',
                prefix='py3o-report-') as out_temp:

            in_temp.write(tmpl_data)
            in_temp.flush()

            template = Template(in_temp.name, out_temp.name)
            template.render(parser_instance.localcontext)

            out_temp.seek(0)

            if filetype.human_ext != 'odt':
                # Now we ask fusion server to convert our template
                fusion_server_obj = pool['py3o.server']
                fusion_server_id = fusion_server_obj.search(
                    cr, uid, [], context=context
                )[0]
                fusion_server = fusion_server_obj.browse(
                    cr, uid, fusion_server_id, context=context
                )
                files = {
                    'tmpl_file': out_temp,
                }
                fields = {
                    "targetformat": filetype.fusion_ext,
                    "datadict": "{}",
                    "image_mapping": "{}",
                    "skipfusion": True,
                }
                r = requests.post(fusion_server.url, data=fields, files=files)
                chunk_size = 1024
                with NamedTemporaryFile(
                    suffix=filetype.human_ext,
                    prefix='py3o-template-'
                ) as fd:
                    for chunk in r.iter_content(chunk_size):
                        fd.write(chunk)
                    fd.seek(0)
                    return fd.read(), filetype.human_ext

            return out_temp.read(), 'odt'

    def create(self, cr, uid, ids, data, context=None):
        """ Override this function to handle our py3o report
        """
        pool = registry(cr.dbname)
        ir_action_report_obj = pool['ir.actions.report.xml']
        report_xml_ids = ir_action_report_obj.search(
            cr, uid, [('report_name', '=', self.name[7:])], context=context
        )
        if not report_xml_ids:
            return super(Py3oParser, self).create(
                cr, uid, ids, data, context=context
            )

        report_xml = ir_action_report_obj.browse(
            cr, uid, report_xml_ids[0], context=context
        )

        result = self.create_source_pdf(
            cr, uid, ids, data, report_xml, context
        )

        if not result:
            return False, False
        return result
