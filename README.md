[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/143/12.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-reporting-engine-143)
[![Build Status](https://travis-ci.org/OCA/reporting-engine.svg?branch=12.0)](https://travis-ci.org/OCA/reporting-engine)
[![Coverage Status](https://img.shields.io/coveralls/OCA/reporting-engine.svg)](https://coveralls.io/r/OCA/reporting-engine?branch=12.0)

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
[bi_sql_editor](bi_sql_editor/) | 12.0.1.2.1 | BI Views builder, based on Materialized or Normal SQL Views
[bi_sql_editor_aggregate](bi_sql_editor_aggregate/) | 12.0.1.1.0 | BI SQL Editor Aggregation
[bi_view_editor](bi_view_editor/) | 12.0.1.1.0 | Graphical BI views builder for Odoo
[kpi](kpi/) | 12.0.1.0.0 | Key Performance Indicator
[kpi_dashboard](kpi_dashboard/) | 12.0.1.3.0 | Create Dashboards using kpis
[kpi_dashboard_altair](kpi_dashboard_altair/) | 12.0.1.0.3 | Create dashboards using altair
[kpi_dashboard_bokeh](kpi_dashboard_bokeh/) | 12.0.1.0.0 | Create dashboards using bokeh
[report_async](report_async/) | 12.0.1.0.1 | Central place to run reports live or async
[report_context](report_context/) | 12.0.1.0.0 | Adding context to reports
[report_csv](report_csv/) | 12.0.1.0.0 | Base module to create csv report
[report_label](report_label/) | 12.0.1.0.0 | Print configurable self-adhesive labels reports
[report_py3o](report_py3o/) | 12.0.2.0.5 | Reporting engine based on Libreoffice (ODT -> ODT, ODT -> PDF, ODT -> DOC, ODT -> DOCX, ODS -> ODS, etc.)
[report_py3o_fusion_server](report_py3o_fusion_server/) | 12.0.1.0.0 | Let the fusion server handle format conversion.
[report_qr](report_qr/) | 12.0.1.0.0 | Web QR Manager
[report_qweb_element_page_visibility](report_qweb_element_page_visibility/) | 12.0.1.0.0 | Report Qweb Element Page Visibility
[report_qweb_parameter](report_qweb_parameter/) | 12.0.1.0.0 | Add new parameters for qweb templates in order to reduce field length and check minimal length
[report_qweb_pdf_fixed_column](report_qweb_pdf_fixed_column/) | 12.0.1.0.0 | Fix auto-col to not change report font size caused by a boundary overflow
[report_qweb_pdf_watermark](report_qweb_pdf_watermark/) | 12.0.1.0.1 | Add watermarks to your QWEB PDF reports
[report_qweb_signer](report_qweb_signer/) | 12.0.1.0.1 | Sign Qweb PDFs usign a PKCS#12 certificate
[report_substitute](report_substitute/) | 12.0.1.0.0 | This module allows to create substitution rules for report actions.
[report_wkhtmltopdf_param](report_wkhtmltopdf_param/) | 12.0.1.0.0 | Add new parameters for a paper format to be used by wkhtmltopdf command as arguments.
[report_xlsx](report_xlsx/) | 12.0.1.0.3 | Base module to create xlsx report
[report_xlsx_helper](report_xlsx_helper/) | 12.0.1.2.0 | Report xlsx helpers
[report_xlsx_helper_demo](report_xlsx_helper_demo/) | 12.0.1.1.0 | Report xlsx helpers - demo
[report_xml](report_xml/) | 12.0.1.0.0 | Allow to generate XML reports

[//]: # (end addons)


## Translation Status

[![Translation status](https://translation.odoo-community.org/widgets/reporting-engine-12-0/-/multi-auto.svg)](https://translation.odoo-community.org/engage/reporting-engine-12-0/?utm_source=widget)

----

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

https://odoo-community.org/
