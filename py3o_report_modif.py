from base64 import b64decode
from tempfile import NamedTemporaryFile as tempfile

from openerp import pooler
from openerp.report.report_sxw import *
from openerp.tools.translate import _
from openerp.osv.osv import except_osv

from py3o.template import Template

from oe_json_serializer import OESerializer

import json
import requests
import os


class py3o_report(report_sxw):
#     def __init__(self, name, table):
#         super(py3o_report, self).__init__(name, table)

    def get_values(self, cr, uid, ids, data, context):
        ''' Override this function to customize the dictionary given to the
        py3o.template renderer. '''

        return {
            'lang': self.get_lang(cr, uid, context),
            'objects': self.getObjects(cr, uid, ids, context),
        }

    def get_lang(self, cr, uid, context):
        pool = pooler.get_pool(cr.dbname)
        lang_obj = pool.get('res.lang')
        user_obj = pool.get('res.users')

        lang_code = user_obj.browse(cr, uid, uid, context=context).lang
        lang = lang_obj.search(cr, uid,
                               [('code', '=', lang_code)],
                               context=context)[0]
        return lang_obj.browse(cr, uid, lang, context=context)

    def format_date(self, date, values):
        ''' Return a date formatted according to the language extracted from
        the "values" argument (which should be the result of get_values). '''
        return date.strftime(values['lang'].date_format)

    def create(self, cr, uid, ids, data, context=None):
        # Find the report definition to get its settings.
        pool = pooler.get_pool(cr.dbname)
        report_xml_obj = pool.get('ir.actions.report.xml')
        report_xml_ids = report_xml_obj.search(cr, uid,
            [('report_name', '=', self.name[7:])],  # Ignore "report."
            context=context)

        if not report_xml_ids:
            return super(py3o_report, self).create(cr, uid, ids, data,
                                                   context=context)
        report_xml = report_xml_obj.browse(cr, uid,
                                           report_xml_ids[0],
                                           context=context)

        template = report_xml.py3o_template_id
        filetype = report_xml.py3o_fusion_filetype


        #Try to request fusion server:

        fusion_server_obj = pool['py3o.server']
        #TODO: Raise a message if no config found
        fusion_server_id = fusion_server_obj.search(
            cr, uid, [], context=context
        )[0]
        fusion_server = fusion_server_obj.browse(cr, uid, fusion_server_id)

        # py3o.template operates on filenames so create temporary files.
        in_temp = tempfile(suffix='.odt', prefix='py3o-template-')

        in_temp.write(b64decode(template.py3o_template_data))
        in_temp.seek(0)
        out_temp = tempfile(suffix='.odt', prefix='py3o-report-')

        # We need to get the variables used in the template
        #TODO: Find a way to avoid calling Template
        t = Template(in_temp.name, out_temp.name)
        # Remove 'py3o.'
        user_variable = [x[5:] for x in t.get_user_variables()]
        print user_variable

        values = self.get_values(cr, uid, ids, data, context)
        print values

        #WARNING: We rely on the fact that there is a for loop on the report
        # on objects (for object in objects) due to lack of time
        val_dict = {}
        for val in values:
            if val == 'objects':
                o = []
                for obj in values[val]:
                    x = OESerializer.serialize(
                        obj,
                        [
                            v[len('object') + 1:]
                            for v in user_variable
                            if v.startswith('object')
                        ]
                    )
                    o.append(x)
                val_dict.update({val: o})
                continue

            x = OESerializer.serialize(
                values[val],
                [
                    v[len(val) + 1:]
                    for v in user_variable
                    if v.startswith(val)
                ]
            )
            val_dict.update({val: x})

        import pprint
        pprint.pprint(val_dict)
        val_json = json.dumps(val_dict)

        fields = {
            'targetformat': filetype.fusion_ext,
            'datadict': val_json,
            'image_mapping': '{}',
        }
        print fields

        r = requests.post(
            fusion_server.url, data=fields, files={'tmpl_file': in_temp}
        )
        in_temp.close()
        if r.status_code == 400:
            raise Exception("Problem with fusion server: %s" % r.json())

        chunk_size = 1024

        ext = filetype.human_ext
        for chunk in r.iter_content(chunk_size):
            out_temp.write(chunk)
        out_temp.seek(0)
        return out_temp.read(), ext
