from openerp.osv import fields, osv


class report_xml(osv.Model):
    ''' Inherit from ir.actions.report.xml to allow customizing the template
    file. The user cam chose a template from a list.
    The list is configurable in the configuration tab, see py3o_template.py
    '''

    _inherit = 'ir.actions.report.xml'

    _columns = {
        'py3o_fusion_filetype': fields.many2one(
            'py3o.fusion.filetype',
            u"Output Format",
        ),
        'py3o_template_id': fields.many2one(
            'py3o.template',
            u"Template",
        ),
    }
