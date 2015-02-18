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
        'report_type': fields.selection(
            [
                ('qweb-pdf', u"PDF"),
                ('qweb-html', u"HTML"),
                ('controller', u"Controller"),
                ('pdf', u"RML pdf (deprecated)"),
                ('sxw', u"RML sxw (deprecated)"),
                ('webkit', u"Webkit (deprecated)"),
                ('py3o', u"Py3o"),
            ],
            string=u"Report Type",
            required=True,
            help=u"HTML will open the report directly in your browser, "
                 u"PDF will use wkhtmltopdf to render the HTML into a PDF "
                 u"file and let you download it, Controller allows you to "
                 u"define the url of a custom controller outputting "
                 u"any kind of report.",
        )
    }
