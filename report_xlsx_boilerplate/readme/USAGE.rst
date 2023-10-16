An example of XLSX report which has a Boilerplate within the module called `module_name`:

A python class ::

    from odoo import models

    class ReportBoilerplateXlsx(models.AbstractModel):
        _name = "report.module_name.report_name"
        _description = "Report Boilerplate"
        _inherit = "report.report_xlsx.abstract"

        _boilerplate_template_file_path = "report/boilerplate_templates/report.xlsx"

**IMPORTANT**
The XLSX Boilerplate file needs to be located inside a folder within the module directory.
