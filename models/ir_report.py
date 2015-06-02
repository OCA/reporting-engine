import os
from openerp.osv import fields, osv
from openerp.report.interface import report_int
from ..py3o_parser import Py3oParser
from openerp import addons


class report_xml(osv.Model):
    """ Inherit from ir.actions.report.xml to allow customizing the template
    file. The user cam chose a template from a list.
    The list is configurable in the configuration tab, see py3o_template.py
    """

    _inherit = 'ir.actions.report.xml'

    _columns = {
        'py3o_fusion_filetype': fields.many2one(
            'py3o.fusion.filetype',
            u"Output Format",
            required=True,
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

    def _lookup_report(self, cr, name):
        """
        Look up a report definition.
        """

        # First lookup in the deprecated place, because if the report
        # definition has not been updated, it is more likely the correct
        # definition is there. Only reports with custom parser
        # specified in Python are still there.
        if 'report.' + name in report_int._reports:
            new_report = report_int._reports['report.' + name]
            if not isinstance(new_report, Py3oParser):
                new_report = None
        else:
            cr.execute(
                'SELECT * '
                'FROM ir_act_report_xml '
                'WHERE report_name=%s AND report_type=%s',
                (name, 'py3o')
            )
            r = cr.dictfetchone()
            if r:
                kwargs = {}
                if r['parser']:
                    kwargs['parser'] = getattr(addons, r['parser'])

                new_report = Py3oParser(
                    'report.' + r['report_name'],
                    r['model'],
                    os.path.join('addons', r['report_rml'] or '/'),
                    header=r['header'],
                    register=False,
                    **kwargs
                )
            else:
                new_report = None

        if new_report:
            return new_report
        else:
            return super(report_xml, self)._lookup_report(cr, name)
