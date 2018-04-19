import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo8-addons-oca-reporting-engine",
    description="Meta package for oca-reporting-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo8-addon-bi_sql_editor',
        'odoo8-addon-bi_view_editor',
        'odoo8-addon-report_custom_filename',
        'odoo8-addon-report_qweb_element_page_visibility',
        'odoo8-addon-report_qweb_signer',
        'odoo8-addon-report_xls',
        'odoo8-addon-report_xlsx',
        'odoo8-addon-report_xml',
        'odoo8-addon-report_xml_sample',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
