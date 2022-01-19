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
    
    <record id="partner_xlsx" model="ir.actions.report">
        <field name="name">Print to XLSX</field>
        <field name="model">res.partner</field>
        <field name="report_type">xlsx</field>
        <field name="report_name">report_xlsx.partner_xlsx</field>
        <field name="report_file">res_partner</field>
    </record>
