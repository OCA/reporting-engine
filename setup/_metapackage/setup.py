import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-reporting-engine",
    description="Meta package for oca-reporting-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-bi_sql_editor',
        'odoo12-addon-bi_sql_editor_aggregate',
        'odoo12-addon-bi_view_editor',
        'odoo12-addon-kpi',
        'odoo12-addon-kpi_dashboard',
        'odoo12-addon-kpi_dashboard_test',
        'odoo12-addon-report_context',
        'odoo12-addon-report_csv',
        'odoo12-addon-report_py3o',
        'odoo12-addon-report_py3o_fusion_server',
        'odoo12-addon-report_qr',
        'odoo12-addon-report_qweb_element_page_visibility',
        'odoo12-addon-report_qweb_parameter',
        'odoo12-addon-report_qweb_pdf_fixed_column',
        'odoo12-addon-report_qweb_pdf_watermark',
        'odoo12-addon-report_qweb_signer',
        'odoo12-addon-report_substitute',
        'odoo12-addon-report_wkhtmltopdf_param',
        'odoo12-addon-report_xlsx',
        'odoo12-addon-report_xlsx_helper',
        'odoo12-addon-report_xlsx_helper_demo',
        'odoo12-addon-report_xml',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
