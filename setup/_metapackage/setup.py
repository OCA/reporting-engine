import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-reporting-engine",
    description="Meta package for oca-reporting-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-base_comment_template',
        'odoo14-addon-bi_sql_editor',
        'odoo14-addon-bi_view_editor',
        'odoo14-addon-kpi_dashboard',
        'odoo14-addon-report_qweb_element_page_visibility',
        'odoo14-addon-report_qweb_encrypt',
        'odoo14-addon-report_qweb_parameter',
        'odoo14-addon-report_qweb_pdf_watermark',
        'odoo14-addon-report_wkhtmltopdf_param',
        'odoo14-addon-report_xlsx',
        'odoo14-addon-report_xlsx_helper',
        'odoo14-addon-report_xlsx_helper_demo',
        'odoo14-addon-report_xml',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
