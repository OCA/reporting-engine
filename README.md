
[![Support the OCA](https://odoo-community.org/readme-banner-image)](https://odoo-community.org/get-involved?utm_source=repo-readme)

# reporting-engine
[![Runboat](https://img.shields.io/badge/runboat-Try%20me-875A7B.png)](https://runboat.odoo-community.org/builds?repo=OCA/reporting-engine&target_branch=16.0)
[![Pre-commit Status](https://github.com/OCA/reporting-engine/actions/workflows/pre-commit.yml/badge.svg?branch=16.0)](https://github.com/OCA/reporting-engine/actions/workflows/pre-commit.yml?query=branch%3A16.0)
[![Build Status](https://github.com/OCA/reporting-engine/actions/workflows/test.yml/badge.svg?branch=16.0)](https://github.com/OCA/reporting-engine/actions/workflows/test.yml?query=branch%3A16.0)
[![codecov](https://codecov.io/gh/OCA/reporting-engine/branch/16.0/graph/badge.svg)](https://codecov.io/gh/OCA/reporting-engine)
[![Translation Status](https://translation.odoo-community.org/widgets/reporting-engine-16-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/reporting-engine-16-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

TODO: add repo description.

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

Available addons
----------------
addon | version | maintainers | summary
--- | --- | --- | ---
[base_comment_template](base_comment_template/) | 16.0.2.3.0 |  | Add conditional mako template to any reporton models that inherits comment.template.
[bi_sql_editor](bi_sql_editor/) | 16.0.2.0.2 | <a href='https://github.com/legalsylvain'><img src='https://github.com/legalsylvain.png' width='32' height='32' style='border-radius:50%;' alt='legalsylvain'/></a> | BI Views builder, based on Materialized or Normal SQL Views
[bi_view_editor](bi_view_editor/) | 16.0.1.1.0 |  | Graphical BI views builder for Odoo
[bi_view_editor_spreadsheet_dashboard](bi_view_editor_spreadsheet_dashboard/) | 16.0.1.0.0 |  | Glue module for BI View Editor and Spreadsheet Dashboard
[report_async](report_async/) | 16.0.1.1.0 | <a href='https://github.com/kittiu'><img src='https://github.com/kittiu.png' width='32' height='32' style='border-radius:50%;' alt='kittiu'/></a> | Central place to run reports live or async
[report_company_details_translatable](report_company_details_translatable/) | 16.0.1.0.0 |  | Report Company Details Translatable
[report_context](report_context/) | 16.0.1.0.0 |  | Adding context to reports
[report_csv](report_csv/) | 16.0.2.1.1 |  | Base module to create csv report
[report_display_name_in_footer](report_display_name_in_footer/) | 16.0.1.1.0 | <a href='https://github.com/Shide'><img src='https://github.com/Shide.png' width='32' height='32' style='border-radius:50%;' alt='Shide'/></a> <a href='https://github.com/rafaelbn'><img src='https://github.com/rafaelbn.png' width='32' height='32' style='border-radius:50%;' alt='rafaelbn'/></a> | Show document name in report footer
[report_docx](report_docx/) | 16.0.1.0.0 | <a href='https://github.com/hbrunn'><img src='https://github.com/hbrunn.png' width='32' height='32' style='border-radius:50%;' alt='hbrunn'/></a> | Create report templates in DOCX and receive DOCX files
[report_footer_html](report_footer_html/) | 16.0.1.0.0 | <a href='https://github.com/Shide'><img src='https://github.com/Shide.png' width='32' height='32' style='border-radius:50%;' alt='Shide'/></a> <a href='https://github.com/rafaelbn'><img src='https://github.com/rafaelbn.png' width='32' height='32' style='border-radius:50%;' alt='rafaelbn'/></a> | Show HTML content in desired Footer Reports
[report_generate_helper](report_generate_helper/) | 16.0.1.0.0 |  | Helper to easily generate report
[report_label](report_label/) | 16.0.1.0.1 | <a href='https://github.com/ivantodorovich'><img src='https://github.com/ivantodorovich.png' width='32' height='32' style='border-radius:50%;' alt='ivantodorovich'/></a> | Print configurable self-adhesive labels reports
[report_paperformat_company_dependent](report_paperformat_company_dependent/) | 16.0.1.0.0 |  | Report Paperformat Company Dependent
[report_partner_address](report_partner_address/) | 16.0.1.0.0 | <a href='https://github.com/yostashiro'><img src='https://github.com/yostashiro.png' width='32' height='32' style='border-radius:50%;' alt='yostashiro'/></a> <a href='https://github.com/aungkokolin1997'><img src='https://github.com/aungkokolin1997.png' width='32' height='32' style='border-radius:50%;' alt='aungkokolin1997'/></a> | Translatable partner address details for reports and portal
[report_py3o](report_py3o/) | 16.0.1.0.6 |  | Reporting engine based on Libreoffice (ODT -> ODT, ODT -> PDF, ODT -> DOC, ODT -> DOCX, ODS -> ODS, etc.)
[report_py3o_fusion_server](report_py3o_fusion_server/) | 16.0.1.0.0 |  | Let the fusion server handle format conversion.
[report_qr](report_qr/) | 16.0.1.0.0 |  | Web QR Manager
[report_qweb_decimal_place](report_qweb_decimal_place/) | 16.0.1.0.0 |  | Report Qweb Decimal Place
[report_qweb_element_page_visibility](report_qweb_element_page_visibility/) | 16.0.1.0.1 |  | Report Qweb Element Page Visibility
[report_qweb_encrypt](report_qweb_encrypt/) | 16.0.1.0.2 | <a href='https://github.com/kittiu'><img src='https://github.com/kittiu.png' width='32' height='32' style='border-radius:50%;' alt='kittiu'/></a> | Allow to encrypt qweb pdfs
[report_qweb_field_option](report_qweb_field_option/) | 16.0.1.0.3 |  | Report Qweb Field Option
[report_qweb_parameter](report_qweb_parameter/) | 16.0.1.0.1 |  | Add new parameters for qweb templates in order to reduce field length and check minimal length
[report_qweb_pdf_cover](report_qweb_pdf_cover/) | 16.0.1.0.0 |  | Add front and back covers to your QWeb PDF reports
[report_qweb_pdf_watermark](report_qweb_pdf_watermark/) | 16.0.1.0.1 |  | Add watermarks to your QWEB PDF reports
[report_qweb_signer](report_qweb_signer/) | 16.0.1.0.5 |  | Sign Qweb PDFs usign a PKCS#12 certificate
[report_substitute](report_substitute/) | 16.0.1.1.2 | <a href='https://github.com/sbejaoui'><img src='https://github.com/sbejaoui.png' width='32' height='32' style='border-radius:50%;' alt='sbejaoui'/></a> | This module allows to create substitution rules for report actions.
[report_text_format_option](report_text_format_option/) | 16.0.1.0.0 |  | Report Text Format Option
[report_wkhtmltopdf_param](report_wkhtmltopdf_param/) | 16.0.1.0.0 |  | Add new parameters for a paper format to be used by wkhtmltopdf command as arguments.
[report_xlsx](report_xlsx/) | 16.0.2.0.2 |  | Base module to create xlsx report
[report_xlsx_helper](report_xlsx_helper/) | 16.0.1.0.0 |  | Report xlsx helpers
[report_xml](report_xml/) | 16.0.1.1.3 |  | Allow to generate XML reports
[sql_export](sql_export/) | 16.0.2.2.1 | <a href='https://github.com/legalsylvain'><img src='https://github.com/legalsylvain.png' width='32' height='32' style='border-radius:50%;' alt='legalsylvain'/></a> <a href='https://github.com/florian-dacosta'><img src='https://github.com/florian-dacosta.png' width='32' height='32' style='border-radius:50%;' alt='florian-dacosta'/></a> | Export data in csv file with SQL requests
[sql_export_delta](sql_export_delta/) | 16.0.1.0.0 | <a href='https://github.com/hbrunn'><img src='https://github.com/hbrunn.png' width='32' height='32' style='border-radius:50%;' alt='hbrunn'/></a> | Support exporting only the changes from last export
[sql_export_excel](sql_export_excel/) | 16.0.1.0.1 |  | Allow to export a sql query to an excel file.
[sql_export_mail](sql_export_mail/) | 16.0.2.1.0 | <a href='https://github.com/legalsylvain'><img src='https://github.com/legalsylvain.png' width='32' height='32' style='border-radius:50%;' alt='legalsylvain'/></a> | Send csv file generated by sql query by mail.
[sql_request_abstract](sql_request_abstract/) | 16.0.1.0.1 | <a href='https://github.com/legalsylvain'><img src='https://github.com/legalsylvain.png' width='32' height='32' style='border-radius:50%;' alt='legalsylvain'/></a> | Abstract Model to manage SQL Requests

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to Odoo Community Association (OCA)
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----
OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
