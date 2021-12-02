[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/143/13.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-reporting-engine-143)
[![Build Status](https://travis-ci.com/OCA/reporting-engine.svg?branch=13.0)](https://travis-ci.com/OCA/reporting-engine)
[![codecov](https://codecov.io/gh/OCA/reporting-engine/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/reporting-engine)
[![Translation Status](https://translation.odoo-community.org/widgets/reporting-engine-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/reporting-engine-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# OCA alternative reporting engines and reporting utilities for Odoo

This repository hosts alternative reporting engines to the ones included on Odoo core (RML, QWeb and Webkit).

The convention is to use a suffix to each module to indicate that it's for using with that report engine (for example, account_invoice_report_birt or sale_order_report_pentaho).

It can contain also another utilities directly involved with reports (like merge/split utils, checkers, signing tools and so on).

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[base_comment_template](base_comment_template/) | 13.0.3.0.1 |  | Add conditional mako template to any report on models that inherits comment.template.
[bi_sql_editor](bi_sql_editor/) | 13.0.1.0.1 |  | BI Views builder, based on Materialized or Normal SQL Views
[kpi](kpi/) | 13.0.1.0.1 |  | Key Performance Indicator
[kpi_dashboard](kpi_dashboard/) | 13.0.1.0.0 | [![etobella](https://github.com/etobella.png?size=30px)](https://github.com/etobella) | Create Dashboards using kpis
[report_batch](report_batch/) | 13.0.1.0.1 | [![bodedra](https://github.com/bodedra.png?size=30px)](https://github.com/bodedra) | Ability to print multiple QWeb reports in a single batch.
[report_context](report_context/) | 13.0.1.0.0 |  | Adding context to reports
[report_csv](report_csv/) | 13.0.1.0.2 |  | Base module to create csv report
[report_layout_config](report_layout_config/) | 13.0.1.0.1 |  | Add possibility to easily modify the global report layout
[report_py3o](report_py3o/) | 13.0.1.0.5 |  | Reporting engine based on Libreoffice (ODT -> ODT, ODT -> PDF, ODT -> DOC, ODT -> DOCX, ODS -> ODS, etc.)
[report_py3o_fusion_server](report_py3o_fusion_server/) | 13.0.1.0.0 |  | Let the fusion server handle format conversion.
[report_qr](report_qr/) | 13.0.1.0.1 |  | Web QR Manager
[report_qweb_element_page_visibility](report_qweb_element_page_visibility/) | 13.0.1.0.1 |  | Report Qweb Element Page Visibility
[report_qweb_parameter](report_qweb_parameter/) | 13.0.1.0.2 |  | Add new parameters for qweb templates in order to reduce field length and check minimal length
[report_qweb_pdf_fixed_column](report_qweb_pdf_fixed_column/) | 13.0.1.0.0 | [![Tardo](https://github.com/Tardo.png?size=30px)](https://github.com/Tardo) | Fix auto-col to not change report font size caused by a boundary overflow
[report_qweb_pdf_watermark](report_qweb_pdf_watermark/) | 13.0.1.0.2 |  | Add watermarks to your QWEB PDF reports
[report_qweb_signer](report_qweb_signer/) | 13.0.2.1.0 |  | Sign Qweb PDFs usign a PKCS#12 certificate
[report_wkhtmltopdf_param](report_wkhtmltopdf_param/) | 13.0.1.0.0 |  | Add new parameters for a paper format to be used by wkhtmltopdf command as arguments.
[report_xlsx](report_xlsx/) | 13.0.1.0.6 |  | Base module to create xlsx report
[report_xlsx_helper](report_xlsx_helper/) | 13.0.1.1.1 |  | Report xlsx helpers
[report_xml](report_xml/) | 13.0.1.0.1 |  | Allow to generate XML reports

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to OCA
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
