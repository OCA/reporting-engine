import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-reporting-engine",
    description="Meta package for oca-reporting-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-base_comment_template>=16.0dev,<16.1dev',
        'odoo-addon-bi_sql_editor>=16.0dev,<16.1dev',
        'odoo-addon-report_company_details_translatable>=16.0dev,<16.1dev',
        'odoo-addon-report_csv>=16.0dev,<16.1dev',
        'odoo-addon-report_label>=16.0dev,<16.1dev',
        'odoo-addon-report_qweb_element_page_visibility>=16.0dev,<16.1dev',
        'odoo-addon-report_wkhtmltopdf_param>=16.0dev,<16.1dev',
        'odoo-addon-report_xlsx>=16.0dev,<16.1dev',
        'odoo-addon-report_xlsx_helper>=16.0dev,<16.1dev',
        'odoo-addon-report_xml>=16.0dev,<16.1dev',
        'odoo-addon-sql_export>=16.0dev,<16.1dev',
        'odoo-addon-sql_export_mail>=16.0dev,<16.1dev',
        'odoo-addon-sql_request_abstract>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
