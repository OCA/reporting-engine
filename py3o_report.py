from tempfile import NamedTemporaryFile

from openerp import addons, pooler
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
            'objects': self.getObjects(cr, uid, ids, context),
        }

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

        # Get the template file.
        template_path = addons.get_module_resource(
            *report_xml.report_file.split('/'))

        # py3o.template operates on filenames so create a temporary file.
        with NamedTemporaryFile(suffix='.odt', prefix='py3o-report-') as \
              temp_file:

            template = Template(template_path, temp_file.name)

            template.render(self.get_values(cr, uid, ids, data, context))

            temp_file.seek(0)
            return temp_file.read(), 'odt'

        return False, False
