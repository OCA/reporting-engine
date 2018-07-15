[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/143/9.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-reporting-engine-143)
[![Build Status](https://travis-ci.org/OCA/reporting-engine.svg?branch=9.0)](https://travis-ci.org/OCA/reporting-engine)
[![Coverage Status](https://img.shields.io/coveralls/OCA/reporting-engine.svg)](https://coveralls.io/r/OCA/reporting-engine?branch=9.0)

OCA alternative reporting engines and reporting utilities for Odoo
==================================================================

This repository hosts alternative reporting engines to the ones included on Odoo core (RML, QWeb and Webkit). It is complemented with the ones that host the reports theirself:

https://github.com/OCA/account-financial-reporting
https://github.com/OCA/purchase-reporting
https://github.com/OCA/sale-reporting
...

The convention is to use a suffix to each module to indicate that it's for using with that report engine (for example, account_invoice_report_birt or sale_order_report_pentaho).

It can contain also another utilities directly involved with reports (like merge/split utils, checkers, signing tools and so on).

[//]: # (addons)

Available addons
----------------
addon | version | summary
--- | --- | ---
[bi_sql_editor](bi_sql_editor/) | 9.0.1.1.0 | BI Views builder, based on Materialized or Normal SQL Views
[bi_view_editor](bi_view_editor/) | 9.0.1.0.0 | Graphical BI views builder for Odoo
[report_custom_filename](report_custom_filename/) | 9.0.1.0.0 | Configure the filename to use when downloading a report
[report_qweb_element_page_visibility](report_qweb_element_page_visibility/) | 9.0.1.0.0 | Report Qweb Element Page Visibility
[report_qweb_pdf_watermark](report_qweb_pdf_watermark/) | 9.0.1.0.1 | Add watermarks to your QWEB PDF reports
[report_wkhtmltopdf_param](report_wkhtmltopdf_param/) | 9.0.1.0.0 | Add new parameters for a paper format to be used by wkhtmltopdf command as arguments.
[report_xlsx](report_xlsx/) | 9.0.1.0.1 | Base module to create xlsx report


Unported addons
---------------
addon | version | summary
--- | --- | ---
[base_report_assembler](base_report_assembler/) | 1.0 (unported) | Base Report Assembler

[//]: # (end addons)

----

OCA, or the Odoo Community Association, is a nonprofit organization whose 
mission is to support the collaborative development of Odoo features and 
promote its widespread use.

http://odoo-community.org/
