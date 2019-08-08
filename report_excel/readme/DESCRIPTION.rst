This module add new report action of report_type = "excel", which will allow user to create excel form or
report with ease (no coding necessary in generating excel file).

This module leverage capability to generate excel file from module **excel_import_export**.

**Report Action** which pass an object + **Dict Instruction** on how to fill data + **Excel template** --> **Output Excel**

For example, creating a print out form will consist of,

1. Create report action for the required model with new report_type = 'excel', and name = <excel_template.xlsx>
2. Create an instruction in XML (or manually set it in XLSX Template). The instruction will tell Odoo how data will be display in the excel file
3. Create a blank excel_template.xlsx, with all heading, labels, formatting or formula as required.

Note:

* This module can ease the development for most reports, but XML instruction can be limited.
  Use **report_xlsx** with total control (by coding)
