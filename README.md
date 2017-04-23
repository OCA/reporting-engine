[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/143/10.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-reporting-engine-143)
[![Build Status](https://travis-ci.org/OCA/reporting-engine.svg?branch=10.0)](https://travis-ci.org/OCA/reporting-engine)
[![Coverage Status](https://img.shields.io/coveralls/OCA/reporting-engine.svg)](https://coveralls.io/r/OCA/reporting-engine?branch=10.0)

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
[report_py3o](report_py3o/) | 10.0.1.1.0 | Reporting engine based on Libreoffice (ODT -> ODT, ODT -> PDF, ODT -> DOC, ODT -> DOCX, ODS -> ODS, etc.)
[report_qweb_element_page_visibility](report_qweb_element_page_visibility/) | 10.0.1.0.0 | Report Qweb Element Page Visibility
[report_xlsx](report_xlsx/) | 10.0.1.0.1 | Base module to create xlsx report


Unported addons
---------------
addon | version | summary
--- | --- | ---
[base_report_assembler](base_report_assembler/) | 1.0 (unported) | Base Report Assembler
[report_xls](report_xls/) | 8.0.0.6.1 (unported) | Excel report engine

[//]: # (end addons)

----

OCA, or the Odoo Community Association, is a nonprofit organization whose 
mission is to support the collaborative development of Odoo features and 
promote its widespread use.

https://odoo-community.org/
