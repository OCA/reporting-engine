from base64 import b64decode
from tempfile import NamedTemporaryFile

from openerp.report.report_sxw import *

from py3o.template import Template

import requests


class py3o_report(report_sxw):
    # def __init__(self, name, table):
    #         super(py3o_report, self).__init__(name, table)

    def get_values(self, cr, uid, ids, data, context):
        """ Override this function to customize the dictionary given to the
        py3o.template renderer. """

        return {
            'lang': self.get_lang(cr, uid, context),
            'objects': self.getObjects(cr, uid, ids, context),
        }

    @staticmethod
    def get_lang(cr, uid, context):
        pool = pooler.get_pool(cr.dbname)
        lang_obj = pool.get('res.lang')
        user_obj = pool.get('res.users')

        lang_code = user_obj.browse(cr, uid, uid, context=context).lang
        lang = lang_obj.search(cr, uid,
                               [('code', '=', lang_code)],
                               context=context)[0]
        return lang_obj.browse(cr, uid, lang, context=context)

    @staticmethod
    def format_date(date, values):
        """ Return a date formatted according to the language extracted from
        the "values" argument (which should be the result of get_values). """
        return date.strftime(values['lang'].date_format)

    def create(self, cr, uid, ids, data, context=None):
        # Find the report definition to get its settings.
        pool = pooler.get_pool(cr.dbname)
        report_xml_obj = pool.get('ir.actions.report.xml')
        report_xml_ids = report_xml_obj.search(cr, uid,
                                               [('report_name', '=', self.name[7:])], # Ignore "report."
                                               context=context)
        if not report_xml_ids:
            return super(py3o_report, self).create(cr, uid, ids, data,
                                                   context=context)
        report_xml = report_xml_obj.browse(cr, uid,
                                           report_xml_ids[0],
                                           context=context)

        template = report_xml.py3o_template_id
        filetype = report_xml.py3o_fusion_filetype

        # py3o.template operates on filenames so create temporary files.
        with NamedTemporaryFile(suffix='.odt', prefix='py3o-template-') as in_temp:

            in_temp.write(b64decode(template.py3o_template_data))
            in_temp.flush()
            in_temp.seek(0)

            template = Template(in_temp.name, None)

            user_instruction_mapping = template.get_user_instructions_mapping()
            values = user_instruction_mapping.jsonify(
                self.get_values(cr, uid, ids, data, context)
            )

            fusion_server_obj = pool['py3o.server']
            fusion_server_id = fusion_server_obj.search(
                cr, uid, [], context=context
            )[0]
            fusion_server = fusion_server_obj.browse(
                cr, uid, fusion_server_id, context=context
            )
            files = {
                'tmpl_file': in_temp,
            }
            fields = {
                "targetformat": filetype.fusion_ext,
                "datadict": values,
                "image_mapping": "{}",
            }
            r = requests.post(fusion_server.url, data=fields, files=files)
            chunk_size = 1024
            with NamedTemporaryFile(
                    suffix=filetype.human_ext,
                    prefix='py3o-template-') as fd:
                for chunk in r.iter_content(chunk_size):
                    fd.write(chunk)
                fd.seek(0)
                return fd.read(), filetype.human_ext
