An example of XLSX report for partners on a module called `module_name`:

A python class ::

    from odoo import models

    class PartnerXlsx(models.AbstractModel):
        _name = 'report.module_name.report_name'
        _inherit = 'report.report_xlsx.abstract'
    
        def generate_xlsx_report(self, workbook, data, partners):
            for obj in partners:
                report_name = obj.name
                # One sheet by partner
                sheet = workbook.add_worksheet(report_name[:31])
                bold = workbook.add_format({'bold': True})
                sheet.write(0, 0, obj.name, bold)

To manipulate the ``workbook`` and ``sheet`` objects, refer to the
`documentation <http://xlsxwriter.readthedocs.org/>`_ of ``xlsxwriter``.

A report XML record ::

    <report 
        id="partner_xlsx"
        model="res.partner"
        string="Print to XLSX"
        report_type="xlsx"
        name="module_name.report_name"
        file="res_partner"
        attachment_use="False"
    />

**XLSX Header & Footer**

You can configure them on the menu *Settings > Technical > Reports > XLSX Header/Footer* following the syntax from 
`xlsxwriter documentation <https://xlsxwriter.readthedocs.io/page_setup.html#set_header>`_.

Example of Header / Footer syntax : ``&LPage &P of &N &CFilename: &F &RSheetname: &A``

On a report XML with ``report_type == 'xlsx'`` you can specified the Header and Footer you configured.
