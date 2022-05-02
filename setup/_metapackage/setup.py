import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo13-addons-oca-reporting-engine",
    description="Meta package for oca-reporting-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo13-addon-base_comment_template',
        'odoo13-addon-bi_sql_editor',
        'odoo13-addon-kpi',
        'odoo13-addon-kpi_dashboard',
        'odoo13-addon-report_async',
        'odoo13-addon-report_batch',
        'odoo13-addon-report_context',
        'odoo13-addon-report_csv',
        'odoo13-addon-report_layout_config',
        'odoo13-addon-report_py3o',
        'odoo13-addon-report_py3o_fusion_server',
        'odoo13-addon-report_qr',
        'odoo13-addon-report_qweb_element_page_visibility',
        'odoo13-addon-report_qweb_parameter',
        'odoo13-addon-report_qweb_pdf_fixed_column',
        'odoo13-addon-report_qweb_pdf_watermark',
        'odoo13-addon-report_qweb_signer',
        'odoo13-addon-report_wkhtmltopdf_param',
        'odoo13-addon-report_xlsx',
        'odoo13-addon-report_xlsx_helper',
        'odoo13-addon-report_xml',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 13.0',
    ]
)
