import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-reporting-engine",
    description="Meta package for oca-reporting-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-bi_sql_editor>=15.0dev,<15.1dev',
        'odoo-addon-report_qr>=15.0dev,<15.1dev',
        'odoo-addon-report_qweb_parameter>=15.0dev,<15.1dev',
        'odoo-addon-report_wkhtmltopdf_param>=15.0dev,<15.1dev',
        'odoo-addon-report_xlsx>=15.0dev,<15.1dev',
        'odoo-addon-report_xlsx_helper>=15.0dev,<15.1dev',
        'odoo-addon-report_xml>=15.0dev,<15.1dev',
        'odoo-addon-sql_export>=15.0dev,<15.1dev',
        'odoo-addon-sql_export_excel>=15.0dev,<15.1dev',
        'odoo-addon-sql_request_abstract>=15.0dev,<15.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 15.0',
    ]
)
