import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo11-addons-oca-reporting-engine",
    description="Meta package for oca-reporting-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo11-addon-bi_sql_editor',
        'odoo11-addon-bi_view_editor',
        'odoo11-addon-report_context',
        'odoo11-addon-report_csv',
        'odoo11-addon-report_fillpdf',
        'odoo11-addon-report_qweb_parameter',
        'odoo11-addon-report_wkhtmltopdf_param',
        'odoo11-addon-report_xlsx',
        'odoo11-addon-report_xlsx_helper',
        'odoo11-addon-report_xlsx_helper_demo',
        'odoo11-addon-report_xml',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
