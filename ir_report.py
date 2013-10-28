from base64 import b64encode

from openerp import addons
from openerp.osv import fields, osv
from openerp.tools.translate import _


class report_xml(osv.osv):
    ''' Inherit from ir.actions.report.xml to allow customizing the template
    file. By default, the file defined when registering the report is used;
    but the user can download / upload a new one. '''

    _inherit = 'ir.actions.report.xml'

    def _get_filename(self, cr, uid, ids, field_name, arg, context):
        return {
                br.id: br.name + '.odt'
                for br in self.browse(cr, uid, ids, context=context)
                if br.report_type == 'py3o'
                }

    def _get_template_data(self, cr, uid, ids, field_name, arg, context):
        ''' Just return the data stored in the binary field, unless it is
        empty; in that case, read the template file. '''

        return {
                br.id: (br.py3o_template_data if br.py3o_template_data
                        else b64encode(file(addons.get_module_resource(
                            *br.report_file.split('/')), 'rb').read()))
                for br in self.browse(cr, uid, ids, context=context)
                if br.report_type == 'py3o'
                }

    _columns = {
        'py3o_filename': fields.function(_get_filename,
                                         type='char',
                                         method=True,
                                         readonly=True),

        'py3o_template': fields.function(_get_template_data,
                                         type='binary',
                                         method=True,
                                         readonly=True),

        'py3o_template_data': fields.binary(_('LibreOffice template')),
    }
