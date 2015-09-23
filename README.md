[![Build Status](https://travis-ci.org/OCA/reporting-engine.svg?branch=8.0)](https://travis-ci.org/OCA/reporting-engine)
[![Coverage Status](https://img.shields.io/coveralls/OCA/reporting-engine.svg)](https://coveralls.io/r/OCA/reporting-engine?branch=8.0)

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
[report_custom_filename](report_custom_filename/) | 1.0 | Configure the filename to use when downloading a report
[report_xls](report_xls/) | 0.6 | Excel report engine

Unported addons
---------------
addon | version | summary
--- | --- | ---
[base_report_assembler](__unported__/base_report_assembler/) | 1.0 (unported) | Base Report Assembler

[//]: # (end addons)

----

OCA, or the Odoo Community Association, is a nonprofit organization whose 
mission is to support the collaborative development of Odoo features and 
promote its widespread use.

http://odoo-community.org/
