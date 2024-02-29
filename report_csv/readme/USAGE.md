An example of CSV report for partners on a module called
\`module_name\`:

A python class :

    from odoo import models

    class PartnerCSV(models.AbstractModel):
        _name = 'report.report_csv.partner_csv'
        _inherit = 'report.report_csv.abstract'

        def generate_csv_report(self, writer, data, partners):
            writer.writeheader()
            for obj in partners:
                writer.writerow({
                    'name': obj.name,
                    'email': obj.email,
                })

        def csv_report_options(self):
            res = super().csv_report_options()
            res['fieldnames'].append('name')
            res['fieldnames'].append('email')
            res['delimiter'] = ';'
            res['quoting'] = csv.QUOTE_ALL
            return res

A report XML record :

    <report
        id="partner_csv"
        model="res.partner"
        string="Print to CSV"
        report_type="csv"
        name="module_name.report_name"
        file="res_partner"
        attachment_use="False"
    />

Update encoding with an appropriate value (e.g. cp932) as necessary.
