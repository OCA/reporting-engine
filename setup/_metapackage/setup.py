import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo9-addons-oca-reporting-engine",
    description="Meta package for oca-reporting-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo9-addon-bi_sql_editor',
        'odoo9-addon-bi_view_editor',
        'odoo9-addon-report_custom_filename',
        'odoo9-addon-report_qweb_element_page_visibility',
        'odoo9-addon-report_qweb_pdf_watermark',
        'odoo9-addon-report_wkhtmltopdf_param',
        'odoo9-addon-report_xlsx',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
