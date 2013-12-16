from base64 import b64decode
from tempfile import NamedTemporaryFile

from openerp import pooler
from openerp.report.report_sxw import *
from openerp.tools.translate import _
from openerp.osv.osv import except_osv

from py3o.template import Template


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

        # py3o.template operates on filenames so create temporary files.
        with NamedTemporaryFile(suffix='.odt', prefix='py3o-template-') as \
            in_temp, \
            NamedTemporaryFile(suffix='.odt', prefix='py3o-report-') as \
            out_temp:

            in_temp.write(b64decode(report_xml.py3o_template))
            in_temp.flush()

            template = Template(in_temp.name, out_temp.name)

            template.render(self.get_values(cr, uid, ids, data, context))

            out_temp.seek(0)
            return out_temp.read(), 'odt'

        return False, False
